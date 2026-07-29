export type Language = "vi" | "en";
export type SidebarMode = "open" | "rail" | "hidden";

export interface ArtifactVersion { version: string; artifact_version: string; prompt_hash: string; tools_hash: string }
export interface Config { providers: string[]; versions: ArtifactVersion[]; default_models: Record<string, string | null>; tools: Array<{name: string; description: string}> }
export interface ToolEvent { tool: string; args: Record<string, unknown>; result: unknown }
export interface Round { round: number; assistant_text?: string | null; tool_calls: Array<{name: string; args: Record<string, unknown>}>; tool_results: ToolEvent[] }
export interface Turn { turn_index: number; user: string; assistant_text?: string | null; status: string; error?: string; started_at: string; ended_at?: string; rounds: Round[]; tool_events: ToolEvent[] }
export interface Session { transcript_id: string; version: string; artifact_version: string; prompt_hash: string; tools_hash: string; provider: string; model?: string | null; created_at: string; updated_at: string; history_window: number; max_tool_rounds: number; turns: Turn[] }
export interface SessionSummary { transcript_id: string; version: string; artifact_version?: string; provider: string; model?: string | null; created_at: string; updated_at: string; turns_count: number; first_user: string; status: string }
export interface StreamEvent { type: string; timestamp?: string; turn_index?: number; round?: number; tool?: string; args?: Record<string, unknown>; result?: unknown; assistant_text?: string; status?: string; error?: string; question?: string; session?: Session }
export interface SessionSettings { provider: string; version: string; model: string; history_window: number; max_tool_rounds: number }
