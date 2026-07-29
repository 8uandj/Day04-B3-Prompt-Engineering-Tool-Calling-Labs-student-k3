import { Braces, Check, ChevronDown, CircleAlert, Cpu, LoaderCircle, Route } from "lucide-react";
import { useState } from "react";
import type { Copy } from "../i18n";
import type { Session, StreamEvent } from "../types";

function JsonDetail({ label, value }: { label: string; value: unknown }) { const [open, setOpen] = useState(false); return <div className="json-detail"><button onClick={() => setOpen(!open)}><Braces size={15}/>{label}<ChevronDown className={open ? "rotated" : ""} size={15}/></button>{open && <pre>{JSON.stringify(value, null, 2)}</pre>}</div> }

export function TracePanel({ copy, session, live }: { copy: Copy; session: Session | null; live: StreamEvent[] }) {
  const rounds = session?.turns.flatMap((turn) => turn.rounds.map((round) => ({ ...round, turn: turn.turn_index }))) ?? [];
  const savedEvents = rounds.flatMap((round) => round.tool_results.map((event) => ({ type: (typeof event.result === "object" && event.result && "error" in event.result) ? "tool_failed" : "tool_completed", turn_index: round.turn, round: round.round, tool: event.tool, args: event.args, result: event.result } as StreamEvent)));
  const events = [...savedEvents, ...live.filter((event) => ["round_started", "tool_started", "tool_completed", "tool_failed", "clarification_required"].includes(event.type))];
  return <section className="workspace-panel trace-panel"><header className="panel-heading"><div><Route/><span>{copy.trace}</span></div><span className="event-count">{events.length}</span></header><div className="trace-scroll">{events.length === 0 ? <div className="empty-state"><div className="empty-icon"><Cpu/></div><h2>{copy.emptyTrace}</h2><p>{copy.emptyTraceHint}</p></div> : <div className="timeline">{events.map((event, index) => {
    const failed = event.type === "tool_failed"; const running = event.type === "tool_started" || event.type === "round_started";
    return <article className={`event-card ${failed ? "event-card--failed" : ""}`} key={`${event.turn_index}-${event.round}-${event.type}-${index}`}>
      <div className={`event-node ${failed ? "event-node--failed" : running ? "event-node--running" : ""}`}>{failed ? <CircleAlert/> : running ? <LoaderCircle className="spin"/> : <Check/>}</div>
      <div className="event-body"><div className="event-header"><strong>{event.tool ?? (event.type === "round_started" ? `Round ${event.round}` : event.type)}</strong><span>T{event.turn_index} · R{event.round ?? "–"}</span></div><small>{event.type.replaceAll("_", " ")}</small>
      {event.args && <JsonDetail label={copy.arguments} value={event.args}/>} {event.result !== undefined && <JsonDetail label={copy.result} value={event.result}/>}</div>
    </article>})}</div>}</div></section>;
}
