import * as Dialog from "@radix-ui/react-dialog";
import { AnimatePresence, motion } from "motion/react";
import { Clock3, History, Search, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { listSessions } from "../api";
import type { Copy } from "../i18n";
import type { SessionSummary } from "../types";

export function HistoryDialog({ copy, onSelect }: { copy: Copy; onSelect: (id: string) => Promise<void> }) {
  const [open, setOpen] = useState(false); const [items, setItems] = useState<SessionSummary[]>([]); const [query, setQuery] = useState(""); const [loading, setLoading] = useState(false);
  useEffect(() => { if (open) { setLoading(true); listSessions().then(setItems).finally(() => setLoading(false)); } }, [open]);
  const filtered = useMemo(() => items.filter((item) => `${item.first_user} ${item.provider} ${item.version}`.toLowerCase().includes(query.toLowerCase())), [items, query]);
  return <Dialog.Root open={open} onOpenChange={setOpen}><Dialog.Trigger asChild><button className="icon-text-button"><History size={18}/><span>{copy.history}</span></button></Dialog.Trigger>
    <Dialog.Portal><Dialog.Overlay className="dialog-overlay"/><AnimatePresence><Dialog.Content asChild><motion.div className="history-dialog" initial={{ opacity: 0, y: 12, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0 }}>
      <div className="dialog-title"><div><Dialog.Title>{copy.history}</Dialog.Title><Dialog.Description>{items.length} sessions</Dialog.Description></div><Dialog.Close className="icon-button" aria-label={copy.close}><X/></Dialog.Close></div>
      <div className="search-field"><Search size={17}/><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={copy.search}/></div>
      <div className="history-list">{loading ? <div className="skeleton-list"/> : filtered.length === 0 ? <div className="dialog-empty"><Clock3/>{copy.noHistory}</div> : filtered.map((item) => <button key={item.transcript_id} className="history-item" onClick={async () => { await onSelect(item.transcript_id); setOpen(false); }}>
        <div><strong>{item.first_user || copy.newChat}</strong><small>{item.provider} · {item.version} · {item.turns_count} {copy.turns.toLowerCase()}</small></div><time>{new Date(item.updated_at).toLocaleString()}</time>
      </button>)}</div>
    </motion.div></Dialog.Content></AnimatePresence></Dialog.Portal>
  </Dialog.Root>;
}
