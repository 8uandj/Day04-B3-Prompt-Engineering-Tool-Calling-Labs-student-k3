from __future__ import annotations

import json

from web.backend.session_store import history_messages, list_sessions, read_session, write_session


def sample_session(identifier="v3_test_1"):
    return {"transcript_id": identifier, "version": "v3", "provider": "openrouter", "model": "test", "created_at": "2026-01-01T10:00:00", "updated_at": "2026-01-01T10:01:00", "turns": [{"turn_index": 1, "user": "First", "assistant_text": "Answer", "status": "answered"}, {"turn_index": 2, "user": "Second", "assistant_text": "Done", "status": "answered"}]}


def test_atomic_write_and_read(tmp_path):
    session = sample_session()
    path = tmp_path / f"{session['transcript_id']}.transcript.json"
    write_session(path, session)
    assert read_session(tmp_path, session["transcript_id"]) == session
    assert not list(tmp_path.glob("*.tmp"))


def test_history_window_keeps_last_pairs():
    assert history_messages(sample_session(), 1) == [{"role": "user", "content": "Second"}, {"role": "assistant", "content": "Done"}]


def test_corrupt_transcript_is_skipped(tmp_path):
    valid = sample_session()
    write_session(tmp_path / "v3_test_1.transcript.json", valid)
    (tmp_path / "broken.transcript.json").write_text("{bad", encoding="utf-8")
    summaries = list_sessions(tmp_path)
    assert len(summaries) == 1
    assert summaries[0]["first_user"] == "First"
