import { PanelLeftOpen, ShieldCheck, Wrench, MessagesSquare, Activity, Languages, History } from "lucide-react";
import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { createSession, getConfig, getSession, streamMessage } from "./api";
import { ChatPanel } from "./components/ChatPanel";
import { Sidebar } from "./components/Sidebar";
import { TracePanel } from "./components/TracePanel";
import { copy } from "./i18n";
import type { Config, Language, Session, SessionSettings, SidebarMode, StreamEvent } from "./types";

const HistoryDialog = lazy(() => import("./components/HistoryDialog"));

const stored = <T,>(key: string, fallback: T): T => { try { return (localStorage.getItem(key) as T | null) ?? fallback; } catch { return fallback; } };

export default function App() {
  const [language, setLanguage] = useState<Language>(() => stored("vin-language", "vi"));
  const [sidebar, setSidebar] = useState<SidebarMode>(() => stored("vin-sidebar", "open"));
  const [config, setConfig] = useState<Config | null>(null); const [session, setSession] = useState<Session | null>(null); const [live, setLive] = useState<StreamEvent[]>([]); const [busy, setBusy] = useState(false); const [pending, setPending] = useState(""); const [historyOpen, setHistoryOpen] = useState(false); const [error, setError] = useState(""); const [mobileTab, setMobileTab] = useState<"chat" | "trace">("chat");
  const [settings, setSettings] = useState<SessionSettings>({ provider: "openrouter", version: "v3", model: "", history_window: 5, max_tool_rounds: 4 });
  const t = copy(language);
  useEffect(() => { getConfig().then((value) => { setConfig(value); setSettings((current) => ({ ...current, model: value.default_models[current.provider] ?? "" })); }).catch((reason) => setError(String(reason))); }, []);
  useEffect(() => localStorage.setItem("vin-language", language), [language]); useEffect(() => localStorage.setItem("vin-sidebar", sidebar), [sidebar]);
  const eventCount = useMemo(() => session?.turns.reduce((sum, turn) => sum + turn.tool_events.length, 0) ?? 0, [session]);
  const send = async (content: string) => { setError(""); setLive([]); setPending(content); setBusy(true); try { const active = session ?? await createSession(settings); if (!session) setSession(active); await streamMessage(active.transcript_id, content, (event) => { if (event.type === "stream_closed" && event.session) { setSession(event.session); setLive([]); } else setLive((items) => [...items, event]); }); } catch (reason) { setError(`${t.streamError} ${String(reason)}`); } finally { setPending(""); setBusy(false); } };
  const restore = async (id: string) => { setSession(await getSession(id)); setLive([]); setError(""); };
  const newChat = () => { setSession(null); setLive([]); setError(""); };
  const artifact = session?.artifact_version ?? config?.versions.find((item) => item.version === settings.version)?.artifact_version ?? "loading";
  return <div className={`app-shell app-shell--${sidebar}`}><Sidebar config={config} copy={t} language={language} mode={sidebar} settings={settings} session={session} onMode={setSidebar} onSettings={setSettings} onLanguage={() => setLanguage(language === "vi" ? "en" : "vi")} onNew={newChat}/>
    {sidebar === "hidden" && <button className="sidebar-reveal" onClick={() => setSidebar("open")} aria-label={t.openSidebar}><PanelLeftOpen/><span>{t.openSidebar}</span></button>}
    <main className="main-content"><header className="topbar"><div className="topbar-title"><span className="live-dot"/><div><strong>Research Command Center</strong><small><ShieldCheck/>Evidence mode</small></div></div><div className="topbar-actions"><button className="language-mobile" onClick={() => setLanguage(language === "vi" ? "en" : "vi")}><Languages/><span>{language.toUpperCase()}</span></button><button className="icon-text-button" aria-label={t.history} onClick={() => setHistoryOpen(true)}><History size={18}/><span>{t.history}</span></button><span className="artifact-chip">{artifact}</span></div></header>
      {historyOpen && <Suspense fallback={null}><HistoryDialog copy={t} open={historyOpen} onOpenChange={setHistoryOpen} onSelect={restore}/></Suspense>}
      <section className="overview"><div><p>VINUNIVERSITY · AI LAB</p><h1>From question to<br/><em>traceable evidence.</em></h1><span>Live tool routing, structured execution traces, and versioned research transcripts.</span></div><div className="metrics"><div><Wrench/><span><strong>{config?.tools.length ?? 0}</strong>{t.tools}</span></div><div><MessagesSquare/><span><strong>{session?.turns.length ?? 0}</strong>{t.turns}</span></div><div><Activity/><span><strong>{eventCount + live.length}</strong>{t.events}</span></div></div></section>
      {error && <div className="error-banner"><span>{error}</span><button onClick={() => setError("")}>×</button></div>}
      <div className="mobile-tabs"><button className={mobileTab === "chat" ? "active" : ""} onClick={() => setMobileTab("chat")}>{t.mobileChat}</button><button className={mobileTab === "trace" ? "active" : ""} onClick={() => setMobileTab("trace")}>{t.mobileTrace}</button></div>
      <div className={`workspace mobile-tab--${mobileTab}`}><ChatPanel copy={t} session={session} busy={busy} pending={pending} onSend={send}/><TracePanel copy={t} session={session} live={live}/></div>
    </main>
  </div>;
}
