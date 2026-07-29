import { motion } from "motion/react";
import { ArrowUp, Bot, LoaderCircle, MessageSquareText, UserRound } from "lucide-react";
import { FormEvent, useState } from "react";
import ReactMarkdown from "react-markdown";
import type { Copy } from "../i18n";
import type { Session } from "../types";

export function ChatPanel({ copy, session, busy, onSend }: { copy: Copy; session: Session | null; busy: boolean; onSend: (message: string) => Promise<void> }) {
  const [value, setValue] = useState(""); const turns = session?.turns ?? [];
  const submit = async (event: FormEvent) => { event.preventDefault(); const content = value.trim(); if (!content || busy) return; setValue(""); await onSend(content); };
  return <section className="workspace-panel chat-panel"><header className="panel-heading"><div><MessageSquareText/><span>{copy.chat}</span></div><span className={`connection ${busy ? "connection--live" : ""}`}>{busy ? copy.connected : copy.ready}</span></header>
    <div className="chat-scroll">{turns.length === 0 ? <div className="empty-state"><div className="empty-icon"><Bot/></div><h2>{copy.emptyChat}</h2><p>{copy.emptyChatHint}</p></div> : turns.map((turn) => <div className="turn" key={turn.turn_index}>
      <motion.div className="message message--user" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}><div className="avatar"><UserRound/></div><div>{turn.user}</div></motion.div>
      {turn.assistant_text && <motion.div className="message message--assistant" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}><div className="avatar avatar--agent">V</div><div className="markdown"><ReactMarkdown>{turn.assistant_text}</ReactMarkdown></div></motion.div>}
      {turn.error && <div className="message-error">{turn.error}</div>}
    </div>)}{busy && <div className="thinking"><LoaderCircle className="spin"/><span>{copy.planning}</span><i/><i/><i/></div>}</div>
    <form className="composer" onSubmit={submit}><textarea rows={1} value={value} onChange={(e) => setValue(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); e.currentTarget.form?.requestSubmit(); } }} placeholder={copy.placeholder} disabled={busy}/><button disabled={busy || !value.trim()} aria-label={copy.send}><ArrowUp/></button></form>
  </section>;
}
