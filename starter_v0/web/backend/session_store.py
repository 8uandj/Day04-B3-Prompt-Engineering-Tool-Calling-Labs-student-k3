from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SESSION_ID = re.compile(r"^[A-Za-z0-9_.-]+$")


class SessionNotFoundError(FileNotFoundError):
    pass


def session_path(transcripts_dir: Path, session_id: str) -> Path:
    if not SESSION_ID.fullmatch(session_id):
        raise SessionNotFoundError(session_id)
    path = transcripts_dir / f"{session_id}.transcript.json"
    if not path.is_file():
        raise SessionNotFoundError(session_id)
    return path


def read_session(transcripts_dir: Path, session_id: str) -> dict[str, Any]:
    return json.loads(session_path(transcripts_dir, session_id).read_text(encoding="utf-8"))


def write_session(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    temporary.replace(path)


def history_messages(session: dict[str, Any], window: int) -> list[dict[str, str]]:
    history: list[dict[str, str]] = []
    for turn in session.get("turns", []):
        if turn.get("user"):
            history.append({"role": "user", "content": str(turn["user"])})
        if turn.get("assistant_text"):
            history.append({"role": "assistant", "content": str(turn["assistant_text"])})
    return history[-window * 2:]


def session_summary(session: dict[str, Any]) -> dict[str, Any]:
    turns = session.get("turns", [])
    first_user = next((str(turn.get("user")) for turn in turns if turn.get("user")), "")
    last_status = turns[-1].get("status") if turns else "empty"
    return {
        "transcript_id": session.get("transcript_id"),
        "version": session.get("version", "draft"),
        "artifact_version": session.get("artifact_version"),
        "provider": session.get("provider"),
        "model": session.get("model"),
        "created_at": session.get("created_at"),
        "updated_at": session.get("updated_at"),
        "turns_count": len(turns),
        "first_user": first_user[:180],
        "status": last_status,
    }


def list_sessions(transcripts_dir: Path) -> list[dict[str, Any]]:
    if not transcripts_dir.exists():
        return []
    summaries: list[dict[str, Any]] = []
    for path in sorted(transcripts_dir.glob("*.transcript.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            summaries.append(session_summary(json.loads(path.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError, TypeError):
            continue
    return summaries
