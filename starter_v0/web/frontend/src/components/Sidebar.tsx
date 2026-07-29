import { ChevronLeft, ChevronRight, EyeOff, Languages, Plus, Settings2, X } from "lucide-react";
import type { Config, Language, Session, SessionSettings, SidebarMode } from "../types";
import type { Copy } from "../i18n";

interface Props { config: Config | null; copy: Copy; language: Language; mode: SidebarMode; settings: SessionSettings; session: Session | null; onMode: (mode: SidebarMode) => void; onSettings: (settings: SessionSettings) => void; onLanguage: () => void; onNew: () => void }

export function Sidebar({ config, copy, language, mode, settings, session, onMode, onSettings, onLanguage, onNew }: Props) {
  const locked = Boolean(session);
  const update = (patch: Partial<SessionSettings>) => onSettings({ ...settings, ...patch });
  return <>{mode !== "hidden" && <>
    <aside className={`sidebar ${mode === "rail" ? "sidebar--rail" : ""}`} aria-label="Application sidebar">
      <div className="brand"><span className="brand-mark">V</span>{mode === "open" && <div><strong>VIN RESEARCH</strong><small>{copy.subtitle}</small></div>}</div>
      <button className="primary-action" onClick={onNew}><Plus size={18}/>{mode === "open" && copy.newChat}</button>
      {mode === "open" ? <div className="settings-stack">
        <div className="section-heading"><Settings2 size={16}/><span>Agent setup</span></div>
        <label>{copy.provider}<select value={settings.provider} disabled={locked} onChange={(e) => update({ provider: e.target.value, model: config?.default_models[e.target.value] ?? "" })}>{config?.providers.map((provider) => <option key={provider}>{provider}</option>)}</select></label>
        <label>{copy.version}<select value={settings.version} disabled={locked} onChange={(e) => update({ version: e.target.value })}>{config?.versions.map((item) => <option key={item.version}>{item.version}</option>)}</select></label>
        <label>{copy.model}<input value={settings.model} disabled={locked} onChange={(e) => update({ model: e.target.value })} placeholder={config?.default_models[settings.provider] ?? "Provider default"}/></label>
        <label>{copy.context}<div className="range-row"><input type="range" min="1" max="10" value={settings.history_window} disabled={locked} onChange={(e) => update({ history_window: Number(e.target.value) })}/><span>{settings.history_window}</span></div></label>
        <label>{copy.rounds}<div className="range-row"><input type="range" min="1" max="8" value={settings.max_tool_rounds} disabled={locked} onChange={(e) => update({ max_tool_rounds: Number(e.target.value) })}/><span>{settings.max_tool_rounds}</span></div></label>
        {locked && <p className="locked-note">{copy.settingsLocked}</p>}
      </div> : <div className="rail-stack"><Settings2/><Languages/></div>}
      <div className="sidebar-footer">
        <button onClick={onLanguage} title={copy.language}><Languages size={18}/>{mode === "open" && <span>{language.toUpperCase()} · {copy.language}</span>}</button>
        <button className="desktop-only" onClick={() => onMode(mode === "open" ? "rail" : "open")} title={mode === "open" ? copy.collapse : copy.expand}>{mode === "open" ? <ChevronLeft/> : <ChevronRight/>}{mode === "open" && <span>{copy.collapse}</span>}</button>
        <button onClick={() => onMode("hidden")} title={copy.hide}>{mode === "open" ? <><EyeOff size={18}/><span>{copy.hide}</span></> : <X/>}</button>
      </div>
    </aside><button className="mobile-overlay" aria-label={copy.close} onClick={() => onMode("hidden")}/>
  </>}</>;
}
