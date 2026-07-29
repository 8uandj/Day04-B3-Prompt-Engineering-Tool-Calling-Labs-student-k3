from __future__ import annotations

import json
from fastapi.testclient import TestClient
from providers.base import ModelResponse
from web.backend import main

class FakeProvider:
    default_model = "fake-model"
    def complete(self, messages, tools, **kwargs):
        return ModelResponse(text="Mock answer")

def test_session_and_sse_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "TRANSCRIPTS", tmp_path)
    monkeypatch.setattr(main, "make_provider", lambda name: FakeProvider())
    client = TestClient(main.app)
    created = client.post("/api/sessions", json={"provider": "openrouter", "version": "v3"})
    assert created.status_code == 201
    session_id = created.json()["transcript_id"]
    with client.stream("POST", f"/api/sessions/{session_id}/messages", json={"content": "Test request"}) as response:
        events = [json.loads(line.removeprefix("data: ")) for line in response.iter_lines() if line.startswith("data: ")]
    assert [event["type"] for event in events] == ["turn_started", "round_started", "assistant_completed", "stream_closed"]
    restored = client.get(f"/api/sessions/{session_id}").json()
    assert restored["turns"][0]["assistant_text"] == "Mock answer"
    assert client.post(f"/api/sessions/{session_id}/messages", json={"content": "   "}).status_code == 422
