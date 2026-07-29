from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from chat import now_iso, run_model_tool_loop, safe_slug
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from web.backend.models import MessageCreate, SessionCreate
from web.backend.session_store import SessionNotFoundError, history_messages, list_sessions, read_session, session_path, write_session


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
TRANSCRIPTS = ROOT / "transcripts"
FRONTEND_DIST = ROOT / "web" / "frontend" / "dist"
PROVIDERS = ("openrouter", "openai", "anthropic", "gemini")
VERSIONS = ("v0", "v1", "v2", "v3")
load_lab_env(ROOT)

app = FastAPI(title="Research Agent API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])
session_locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


def sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config")
def config() -> dict[str, Any]:
    declarations = load_tool_declarations(ARTIFACTS / "tools.yaml")
    artifacts = [artifact_version_dict(build_artifact_version(version, ARTIFACTS / "system_prompt.md", ARTIFACTS / "tools.yaml")) for version in VERSIONS]
    models = {name: getattr(make_provider(name), "default_model", None) for name in PROVIDERS}
    return {"providers": PROVIDERS, "versions": artifacts, "default_models": models, "tools": declarations}


@app.post("/api/sessions", status_code=201)
def create_session(payload: SessionCreate) -> dict[str, Any]:
    provider = make_provider(payload.provider)
    model = payload.model or getattr(provider, "default_model", None)
    artifact = build_artifact_version(payload.version, ARTIFACTS / "system_prompt.md", ARTIFACTS / "tools.yaml")
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join((safe_slug(payload.version), safe_slug(payload.provider), stamp))
    session = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": payload.provider,
        "model": model,
        "system_prompt": str(ARTIFACTS / "system_prompt.md"),
        "tools": str(ARTIFACTS / "tools.yaml"),
        "history_window": payload.history_window,
        "max_tool_rounds": payload.max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    path = TRANSCRIPTS / f"{transcript_id}.transcript.json"
    write_session(path, session)
    return session


@app.get("/api/sessions")
def sessions() -> list[dict[str, Any]]:
    return list_sessions(TRANSCRIPTS)


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    try:
        return read_session(TRANSCRIPTS, session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Transcript is invalid") from exc


async def stream_turn(session_id: str, payload: MessageCreate) -> AsyncIterator[str]:
    async with session_locks[session_id]:
        try:
            session = read_session(TRANSCRIPTS, session_id)
            path = session_path(TRANSCRIPTS, session_id)
        except SessionNotFoundError:
            yield sse({"type": "turn_failed", "error": "Session not found", "timestamp": now_iso()})
            return

        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        turn_index = len(session.get("turns", [])) + 1

        def emit(event: dict[str, Any]) -> None:
            loop.call_soon_threadsafe(queue.put_nowait, {**event, "turn_index": turn_index})

        def worker() -> None:
            turn: dict[str, Any] = {"turn_index": turn_index, "started_at": now_iso(), "user": payload.content.strip(), "status": "started", "assistant_text": None, "rounds": [], "tool_events": []}
            try:
                prompt = (ARTIFACTS / "system_prompt.md").read_text(encoding="utf-8")
                messages = [{"role": "system", "content": prompt}, *history_messages(session, int(session.get("history_window", 5))), {"role": "user", "content": payload.content.strip()}]
                provider = make_provider(str(session["provider"]))
                declarations = load_tool_declarations(ARTIFACTS / "tools.yaml")
                result = run_model_tool_loop(provider=provider, messages=messages, tools=to_openai_tools(declarations), model=session.get("model"), max_tool_rounds=int(session.get("max_tool_rounds", 4)), event_callback=emit)
                turn.update(result)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                turn.update({"status": "provider_error", "error": error})
                emit({"type": "turn_failed", "timestamp": now_iso(), "error": error})
            finally:
                turn["ended_at"] = now_iso()
                session.setdefault("turns", []).append(turn)
                session["updated_at"] = now_iso()
                write_session(path, session)
                loop.call_soon_threadsafe(queue.put_nowait, {"type": "stream_closed", "turn_index": turn_index, "session": session})

        task = asyncio.create_task(asyncio.to_thread(worker))
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=15)
            except asyncio.TimeoutError:
                yield ": ping\n\n"
                continue
            if event.get("type") == "stream_closed":
                yield sse(event)
                break
            yield sse(event)
        await task


@app.post("/api/sessions/{session_id}/messages")
def post_message(session_id: str, payload: MessageCreate) -> StreamingResponse:
    try:
        session_path(TRANSCRIPTS, session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc
    return StreamingResponse(stream_turn(session_id, payload), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if FRONTEND_DIST.is_dir():
    assets = FRONTEND_DIST / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str) -> FileResponse:
        candidate = (FRONTEND_DIST / path).resolve()
        if path and candidate.is_file() and FRONTEND_DIST.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/", include_in_schema=False)
    def frontend_missing() -> JSONResponse:
        return JSONResponse({"message": "Frontend is not built. Run npm install && npm run build in web/frontend."})
