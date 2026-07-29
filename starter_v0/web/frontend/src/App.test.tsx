import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import App from "./App";

vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ providers: ["openrouter"], versions: [{ version: "v3", artifact_version: "v3+p123+t456", prompt_hash: "123", tools_hash: "456" }], default_models: { openrouter: "test-model" }, tools: [] }), { status: 200, headers: { "Content-Type": "application/json" } })));

test("sidebar can hide, reveal, and switch language", async () => {
  localStorage.clear();
  render(<App/>);
  expect(screen.getByText("Research Command Center")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Ẩn sidebar" }));
  const reveal = screen.getByRole("button", { name: "Mở sidebar" });
  expect(reveal).toBeInTheDocument();
  fireEvent.click(reveal);
  fireEvent.click(screen.getByRole("button", { name: /English/ }));
  expect(screen.getByRole("button", { name: /new conversation/i })).toBeInTheDocument();
});
