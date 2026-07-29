from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS = ROOT / "artifacts"
TRANSCRIPTS = ROOT / "transcripts"
load_lab_env(ROOT)
st.set_page_config(page_title="Research Command Center", page_icon="◆", layout="wide")


def apply_theme() -> None:
    st.markdown("""<style>
:root{--blue:#003b71;--navy:#00264c;--red:#d71920;--ink:#112033;--muted:#6e7b8b;--mist:#f4f7fb;--line:#dce5f0} .stApp{background:var(--mist);color:var(--ink)} #MainMenu,footer,header{visibility:hidden}.block-container{max-width:1440px;padding:1.4rem 2rem 2.5rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#002d58,#001d3b)}[data-testid="stSidebar"] label,[data-testid="stSidebar"] p,[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{color:#f8fbff!important}[data-testid="stSidebar"] [data-baseweb="select"]>div,[data-testid="stSidebar"] [data-baseweb="input"]>div,[data-testid="stSidebar"] input{color:var(--ink)!important;background:#fff!important}[data-testid="stSidebar"] [data-baseweb="select"] svg{fill:var(--navy)!important}
.hero{position:relative;overflow:hidden;padding:1.65rem 1.8rem;border-radius:20px;color:#fff;background:linear-gradient(118deg,#00264c,#004f91 66%,#1479b8);box-shadow:0 16px 32px rgba(0,42,84,.18);margin-bottom:1.15rem}.hero:after{content:"";position:absolute;width:230px;height:230px;right:-55px;top:-118px;border:34px solid rgba(255,255,255,.1);border-radius:50%}.eyebrow{color:#a9d9ff;font-size:.73rem;letter-spacing:.13em;font-weight:750;margin-bottom:.35rem}.hero h1{font-size:clamp(1.45rem,3vw,2.25rem);line-height:1.12;margin:0;letter-spacing:-.035em}.hero p{max-width:680px;margin:.65rem 0;color:#d9ecfc}.pill{display:inline-block;margin-top:.75rem;padding:.35rem .66rem;border:1px solid rgba(255,255,255,.28);border-radius:999px;background:rgba(255,255,255,.1);font:600 .78rem/1 monospace}
.metric{min-height:92px;padding:1rem;background:#fff;border:1px solid var(--line);border-radius:15px;box-shadow:0 4px 14px rgba(18,48,79,.045);transition:.2s}.metric:hover{transform:translateY(-3px);box-shadow:0 12px 24px rgba(18,48,79,.11)}.metric-label{color:var(--muted);font-size:.75rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase}.metric-value{font-size:1.22rem;font-weight:760;margin-top:.3rem;color:var(--navy)}
.label{margin:1.35rem 0 .55rem;color:var(--navy);font-size:1rem;font-weight:760}.empty{text-align:center;padding:2.6rem 1rem;border:1px dashed #b6c7d9;border-radius:16px;color:var(--muted);background:rgba(255,255,255,.55)}.trace{margin:.65rem 0;padding:1rem;border:1px solid var(--line);border-left:4px solid var(--blue);border-radius:12px;background:#fff;transition:.18s}.trace:hover{transform:translateX(4px);border-left-color:var(--red);box-shadow:0 10px 22px rgba(0,38,76,.08)}.tool{font-family:ui-monospace,monospace;background:#eaf3fa;color:#003b71;padding:.12rem .36rem;border-radius:5px}.meta{color:var(--muted);font-size:.84rem;margin-top:.4rem}.dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--red);margin-right:.55rem;box-shadow:0 0 0 4px #fee9ea}
.stButton>button{border:0;border-radius:9px;background:var(--red);color:#fff;font-weight:700;transition:.18s}.stButton>button:hover{background:#b10f16;transform:translateY(-2px);box-shadow:0 8px 18px rgba(215,25,32,.25)}[data-testid="stChatInput"]{border:1px solid #b8cadc;border-radius:14px;box-shadow:0 6px 18px rgba(0,38,76,.08)}@media(max-width:760px){.block-container{padding:.8rem}.hero{padding:1.3rem;border-radius:14px}}
</style>""", unsafe_allow_html=True)


def init_state() -> None:
    for key, value in {"messages": [], "turns": [], "history": [], "transcript": None}.items():
        st.session_state.setdefault(key, value)


def transcript(version: str, provider: str, model: str | None) -> dict[str, Any]:
    artifact = build_artifact_version(version, ARTIFACTS / "system_prompt.md", ARTIFACTS / "tools.yaml")
    identifier = "_".join((safe_slug(version), safe_slug(provider), datetime.now().strftime("%Y%m%dT%H%M%S%f")))
    return {"transcript_id": identifier, **artifact_version_dict(artifact), "provider": provider, "model": model, "system_prompt": str(ARTIFACTS / "system_prompt.md"), "tools": str(ARTIFACTS / "tools.yaml"), "created_at": now_iso(), "updated_at": now_iso(), "turns": []}


def save() -> None:
    data = st.session_state.transcript
    if data:
        write_transcript(TRANSCRIPTS / f"{data['transcript_id']}.transcript.json", data)


def inspect_json(label: str, data: Any) -> None:
    with st.expander(label):
        st.code(json.dumps(data, ensure_ascii=False, indent=2, default=str), language="json")


def render_trace(turns: list[dict[str, Any]]) -> None:
    st.markdown('<div class="label">Tool-calling trace</div>', unsafe_allow_html=True)
    if not turns:
        st.markdown('<div class="empty">Trace sẽ xuất hiện ở đây sau khi agent thực hiện một lượt chat.</div>', unsafe_allow_html=True)
        return
    for turn in reversed(turns):
        with st.expander(f"Turn {turn['turn_index']} · {turn['status']}", expanded=turn is turns[-1]):
            for round_data in turn.get("rounds", []):
                calls = round_data.get("tool_calls", [])
                st.caption(f"Round {round_data['round']} · {len(calls)} tool call(s)")
                for event in round_data.get("tool_results", []):
                    result = event.get("result", {})
                    failed = isinstance(result, dict) and "error" in result
                    st.markdown(f'<div class="trace"><b><span class="dot"></span><span class="tool">{event.get("tool", "unknown")}</span> · {"error" if failed else "completed"}</b><div class="meta">Arguments and tool result, recorded for audit.</div></div>', unsafe_allow_html=True)
                    a, b = st.columns(2)
                    with a: inspect_json("Arguments", event.get("args", {}))
                    with b: inspect_json("Error result" if failed else "Result", result)
                if not calls:
                    st.caption("No tool called — the agent answered directly.")


apply_theme(); init_state()
with st.sidebar:
    st.markdown("### ◆ Research Agent\nLive tool-calling workspace for evaluation, evidence, and demo rehearsal.")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"])
    version = st.selectbox("Artifact version", ["v0", "v1", "v2", "v3"], index=3, help="Version label stored in the transcript.")
    model_override = st.text_input("Model override (optional)", placeholder="Provider default")
    history_window = st.slider("Context turns", 1, 10, 5)
    max_tool_rounds = st.slider("Max tool rounds", 1, 8, 4)
    if st.button("New conversation", use_container_width=True):
        st.session_state.messages, st.session_state.turns, st.session_state.history, st.session_state.transcript = [], [], [], None
        st.rerun()
    if st.session_state.transcript:
        st.download_button("Download transcript", json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2), file_name=f"{st.session_state.transcript['transcript_id']}.transcript.json", mime="application/json", use_container_width=True)

try:
    declarations = load_tool_declarations(ARTIFACTS / "tools.yaml")
except Exception as exc:
    st.error(f"Cannot load artifacts/tools.yaml: {type(exc).__name__}: {exc}"); st.stop()

active = st.session_state.transcript.get("artifact_version", "Ready to run") if st.session_state.transcript else "Ready to run"
st.markdown(f'<section class="hero"><div class="eyebrow">VINUNIVERSITY · AI LAB DAY 04</div><h1>Research Agent<br>Command Center</h1><p>Run live research conversations, inspect tool decisions, and keep versioned evidence ready for demo.</p><span class="pill">{active}</span></section>', unsafe_allow_html=True)
for column, (name, value) in zip(st.columns(3), [("Declared tools", len(declarations)), ("Chat turns", len(st.session_state.turns)), ("Tool events", sum(len(t.get("tool_events", [])) for t in st.session_state.turns))]):
    column.markdown(f'<div class="metric"><div class="metric-label">{name}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

chat_col, trace_col = st.columns((1.18, 1), gap="large")
with chat_col:
    st.markdown('<div class="label">Live conversation</div>', unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown('<div class="empty">Start with a research request. Every decision will appear in the trace panel.</div>', unsafe_allow_html=True)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])
with trace_col: render_trace(st.session_state.turns)

if user_text := st.chat_input("Ask the research agent…"):
    st.session_state.messages.append({"role": "user", "content": user_text})
    try:
        provider = make_provider(provider_name)
        selected_model = model_override.strip() or getattr(provider, "default_model", None)
        if st.session_state.transcript is None:
            st.session_state.transcript = transcript(version.strip() or "draft", provider_name, selected_model)
            st.session_state.transcript.update({"history_window": history_window, "max_tool_rounds": max_tool_rounds})
        prompt = (ARTIFACTS / "system_prompt.md").read_text(encoding="utf-8")
        messages = [{"role": "system", "content": prompt}, *trim_history(st.session_state.history, history_window), {"role": "user", "content": user_text}]
        turn = {"turn_index": len(st.session_state.turns) + 1, "started_at": now_iso(), "user": user_text, "status": "started", "rounds": [], "tool_events": []}
        with st.spinner("Planning tool calls…"):
            result = run_model_tool_loop(provider=provider, messages=messages, tools=to_openai_tools(declarations), model=model_override.strip() or None, max_tool_rounds=max_tool_rounds)
        turn.update(result); turn["ended_at"] = now_iso()
        st.session_state.turns.append(turn); st.session_state.transcript["turns"].append(turn)
        st.session_state.messages.append({"role": "assistant", "content": result["assistant_text"]})
        st.session_state.history.extend(({"role": "user", "content": user_text}, {"role": "assistant", "content": result["assistant_text"]}))
        save(); st.rerun()
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        st.error(f"Provider/tool execution failed: {error}")
        if st.session_state.transcript:
            failed = {"turn_index": len(st.session_state.turns) + 1, "started_at": now_iso(), "ended_at": now_iso(), "user": user_text, "status": "provider_error", "error": error, "rounds": [], "tool_events": []}
            st.session_state.turns.append(failed); st.session_state.transcript["turns"].append(failed); save()
