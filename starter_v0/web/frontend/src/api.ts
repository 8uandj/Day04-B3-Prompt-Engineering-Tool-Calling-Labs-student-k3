import type { Config, Session, SessionSettings, SessionSummary, StreamEvent } from "./types";

async function json<T>(response: Response): Promise<T> {
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? `HTTP ${response.status}`);
  return response.json() as Promise<T>;
}

export const getConfig = () => fetch("/api/config").then(json<Config>);
export const listSessions = () => fetch("/api/sessions").then(json<SessionSummary[]>);
export const getSession = (id: string) => fetch(`/api/sessions/${encodeURIComponent(id)}`).then(json<Session>);
export const createSession = (settings: SessionSettings) => fetch("/api/sessions", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(settings) }).then(json<Session>);

export async function streamMessage(id: string, content: string, onEvent: (event: StreamEvent) => void): Promise<void> {
  const response = await fetch(`/api/sessions/${encodeURIComponent(id)}/messages`, { method: "POST", headers: { "Content-Type": "application/json", Accept: "text/event-stream" }, body: JSON.stringify({ content }) });
  if (!response.ok || !response.body) throw new Error((await response.json().catch(() => null))?.detail ?? `HTTP ${response.status}`);
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const blocks = buffer.split("\\n\\n");
    buffer = blocks.pop() ?? "";
    for (const block of blocks) {
      const payload = block.split("\\n").filter((line) => line.startsWith("data:")).map((line) => line.slice(5).trim()).join("");
      if (payload) onEvent(JSON.parse(payload) as StreamEvent);
    }
  }
}
