from __future__ import annotations

from providers.base import ModelResponse, ToolCall
import chat


class SequenceProvider:
    def __init__(self, responses):
        self.responses = iter(responses)

    def complete(self, messages, tools, **kwargs):
        return next(self.responses)


def test_answer_emits_operational_events():
    events = []
    result = chat.run_model_tool_loop(provider=SequenceProvider([ModelResponse(text="Done")]), messages=[{"role": "user", "content": "hello"}], tools=[], model=None, max_tool_rounds=2, event_callback=events.append)
    assert result["status"] == "answered"
    assert [event["type"] for event in events] == ["turn_started", "round_started", "assistant_completed"]


def test_tool_events_include_success(monkeypatch):
    monkeypatch.setitem(chat.TOOL_FUNCTIONS, "unit_tool", lambda value: {"value": value})
    provider = SequenceProvider([ModelResponse(tool_calls=[ToolCall(name="unit_tool", args={"value": 7})]), ModelResponse(text="Final")])
    events = []
    result = chat.run_model_tool_loop(provider=provider, messages=[{"role": "user", "content": "run"}], tools=[], model=None, max_tool_rounds=2, event_callback=events.append)
    assert result["tool_events"][0]["result"] == {"value": 7}
    assert [event["type"] for event in events] == ["turn_started", "round_started", "tool_started", "tool_completed", "round_started", "assistant_completed"]


def test_clarification_pauses_the_turn(monkeypatch):
    monkeypatch.setitem(chat.TOOL_FUNCTIONS, "ask", lambda question: {"awaiting_user": True, "question": question})
    events = []
    result = chat.run_model_tool_loop(provider=SequenceProvider([ModelResponse(tool_calls=[ToolCall(name="ask", args={"question": "Which topic?"})])]), messages=[{"role": "user", "content": "research"}], tools=[], model=None, max_tool_rounds=2, event_callback=events.append)
    assert result["status"] == "waiting_for_user"
    assert result["assistant_text"] == "Which topic?"
    assert "clarification_required" in [event["type"] for event in events]
