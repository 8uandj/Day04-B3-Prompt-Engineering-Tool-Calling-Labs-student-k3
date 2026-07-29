import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import App from "./App";

vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ providers: ["openrouter"], versions: [{ version: "v3", artifact_version: "v3+p123+t456", prompt_hash: "123", tools_hash: "456" }], default_models: { openrouter: "test-model" }, tools: [] }), { status: 200, headers: { "Content-Type": "application/json" } })));

test("renders the command center and persistent sidebar controls", async () => {
  render(<App/>);
  expect(screen.getByText("Research Command Center")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /cuộc trò chuyện mới/i })).toBeInTheDocument();
});
