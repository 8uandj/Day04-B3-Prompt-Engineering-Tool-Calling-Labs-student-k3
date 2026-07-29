import { ArrowUp, Bot, LoaderCircle, MessageSquareText, UserRound } from "lucide-react";
import { FormEvent, lazy, Suspense, useState } from "react";
import type { Copy } from "../i18n";
import type { Session } from "../types";

const MarkdownContent = lazy(() => import("./MarkdownContent"));

export function ChatPanel({ copy, session, busy, pending, onSend }: { copy: Copy; session: Session | null; busy: boolean; pending: string; onSend: (message: string) => Promise<void> }) {
  const [value, setValue] = useState(""); const turns = session?.turns ?? [];
  const submit = async (event: FormEvent) => { event.preventDefault(); const content = value.trim(); if (!content || busy) return; setValue(""); await onSend(content); };
  return <section className="workspace-panel chat-panel"><header className="panel-heading"><div><MessageSquareText/><span>{copy.chat}</span></div><span className={`connection ${busy ? "connection--live" : ""}`}>{busy ? copy.connected : copy.ready}</span></header>
    <div className="chat-scroll">{turns.length === 0 ? <div className="empty-state"><div className="empty-icon"><Bot/></div><h2>{copy.emptyChat}</h2><p>{copy.emptyChatHint}</p></div> : turns.map((turn) => <div className="turn" key={turn.turn_index}>
      <div className="message message--user"><div className="avatar"><UserRound/></div><div>{turn.user}</div></div>
      {turn.assistant_text && <div className="message message--assistant"><div className="avatar avatar--agent">V</div><div className="markdown"><Suspense fallback={<span>{turn.assistant_text}</span>}><MarkdownContent content={turn.assistant_text}/></Suspense></div></div>}
      {turn.error && <div className="message-error">{turn.error}</div>}
    </div>)}{pending && <div className="message message--user"><div className="avatar"><UserRound/></div><div>{pending}</div></div>}{busy && <div className="thinking"><LoaderCircle className="spin"/><span>{copy.planning}</span><i/><i/><i/></div>}</div>
    <form className="composer" onSubmit={submit}><textarea rows={1} value={value} onChange={(e) => setValue(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); e.currentTarget.form?.requestSubmit(); } }} placeholder={copy.placeholder} disabled={busy}/><button disabled={busy || !value.trim()} aria-label={copy.send}><ArrowUp/></button></form>
  </section>;
}
