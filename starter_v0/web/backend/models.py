from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


ProviderName = Literal["openrouter", "openai", "anthropic", "gemini"]
ArtifactLabel = Literal["v0", "v1", "v2", "v3"]


class SessionCreate(BaseModel):
    provider: ProviderName = "openrouter"
    version: ArtifactLabel = "v3"
    model: str | None = Field(default=None, max_length=160)
    history_window: int = Field(default=5, ge=1, le=10)
    max_tool_rounds: int = Field(default=4, ge=1, le=8)


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=12000)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be blank")
        return value
