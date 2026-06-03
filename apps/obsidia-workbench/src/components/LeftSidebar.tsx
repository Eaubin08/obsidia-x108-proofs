// OBSIDIA-UI-IMPROVEMENT: LeftSidebar — groups, collapse 44px, hover popover
import { useState, useEffect } from 'react'
import {
  MessageSquare, Database, Settings, Plus, Shield, FileCode,
  Coins, Globe, Link, ClipboardList, ArrowRight, Trash2,
  ChevronLeft, ChevronRight, Search,
} from 'lucide-react'
import { MEMORY_SOURCES, NON_SOVEREIGNTY_BADGES } from '../data/mockData'
import type { StoredSession } from '../lib/sessionStore'
import { deleteSession, getSessions } from '../lib/sessionStore'

export type ViewId =
  | 'chat' | 'memory' | 'graphiti' | 'x108' | 'os3'
  | 'gencoin' | 'worldcall' | 'blockchain' | 'audit' | 'settings' | 'translation' | 'health'
  | 'runtime-wiring'

const GROUPS: { label: string; items: { id: ViewId; label: string; icon: typeof MessageSquare }[] }[] = [
  {
    label: 'CORE',
    items: [
      { id: 'chat' as ViewId,    label: 'CHAT',     icon: MessageSquare },
      { id: 'x108' as ViewId,    label: 'X-108',    icon: Shield },
      { id: 'memory' as ViewId,  label: 'MEMORY',   icon: Database },
    ],
  },
  {
    label: 'PROOFS',
    items: [
      { id: 'os3' as ViewId,         label: 'OS3',         icon: FileCode },
      { id: 'audit' as ViewId,       label: 'AUDIT',       icon: ClipboardList },
      { id: 'blockchain' as ViewId,   label: 'BLOCKCHAIN',  icon: Link },
    ],
  },
  {
    label: 'DATA',
    items: [
      { id: 'graphiti' as ViewId,    label: 'GRAPHITI',    icon: Search },
      { id: 'gencoin' as ViewId,     label: 'GENCOIN',     icon: Coins },
      { id: 'worldcall' as ViewId,   label: 'WORLDCALL',   icon: Globe },
    ],
  },
  {
    label: 'ADMIN',
    items: [
      { id: 'settings' as ViewId,    label: 'SETTINGS',    icon: Settings },
      { id: 'translation' as ViewId, label: 'OS TRAD',     icon: ArrowRight },
      { id: 'health' as ViewId,      label: 'HEALTH',      icon: Shield },
    ],
  },
  {
    label: 'WIRING',
    items: [
      { id: 'runtime-wiring' as ViewId, label: 'RT WIRING', icon: Shield },
    ],
  },
]

const BADGE_CLS: Record<string, string> = {
  kernel:  'obs-badge-kernel',   proof: 'obs-badge-proof',
  brody:   'obs-badge-brody',    memory: 'obs-badge-memory',
  gencoin: 'obs-badge-gencoin',  pass: 'obs-badge-pass',
}

const COLLAPSE_KEY = 'obsidia-sidebar-collapsed'

interface Props {
  activeView: ViewId
  onViewChange: (v: ViewId) => void
  sessions: StoredSession[]
  activeSessionId: string
  onNewSession: () => void
  onSelectSession: (id: string) => void
}

function SessionPopover({ s }: { s: StoredSession }) {
  return (
    <div className="absolute left-full ml-2 top-0 z-50 w-48 p-2 bg-obs-surface border border-obs-border rounded-lg shadow-xl hidden group-hover:block">
      <div className="text-obs-text text-[10px] font-mono mb-1 truncate">{s.preview.slice(0, 60)}</div>
      <div className="text-obs-dtext text-[8px] font-mono">
        {new Date(s.lastMessageAt).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })}
      </div>
      <div className="text-obs-muted text-[8px] font-mono mt-0.5">mode: {s.backendMode ?? 'MOCK'}</div>
    </div>
  )
}

export function LeftSidebar({
  activeView, onViewChange, sessions, activeSessionId, onNewSession, onSelectSession,
}: Props) {
  const [, forceUpdate] = useState(0)
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem(COLLAPSE_KEY) === 'true')

  useEffect(() => { localStorage.setItem(COLLAPSE_KEY, String(collapsed)) }, [collapsed])

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    deleteSession(id)
    forceUpdate(n => n + 1)
    if (id === activeSessionId) onNewSession()
  }

  if (collapsed) {
    return (
      <aside className="w-[44px] bg-obs-surface border-r border-obs-border flex flex-col items-center gap-1 py-2 shrink-0">
        <button onClick={() => setCollapsed(false)} className="p-1 text-obs-dtext hover:text-obs-text" title="Expand sidebar">
          <ChevronRight size={12} />
        </button>
        {GROUPS.flatMap(g => g.items).map(item => {
          const Icon = item.icon
          const active = activeView === item.id
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`p-1.5 rounded ${active ? 'bg-obs-border text-obs-brody' : 'text-obs-dtext hover:text-obs-mtext'}`}
              title={item.label}
            >
              <Icon size={14} />
            </button>
          )
        })}
      </aside>
    )
  }

  return (
    <aside className="w-60 bg-obs-surface border-r border-obs-border flex flex-col overflow-hidden shrink-0">
      {/* Collapse button */}
      <div className="flex items-center justify-between px-2 py-1 border-b border-obs-border">
        <span className="text-obs-dtext font-mono text-[9px]">Navigation</span>
        <button onClick={() => setCollapsed(true)} className="p-0.5 text-obs-dtext hover:text-obs-text" title="Collapse sidebar">
          <ChevronLeft size={11} />
        </button>
      </div>

      {/* Module groups */}
      <div className="px-2 py-2 border-b border-obs-border">
        {GROUPS.map(group => (
          <div key={group.label} className="mb-2 last:mb-0">
            <div className="text-[8px] font-mono text-obs-dtext uppercase tracking-wider px-1 mb-1">{group.label}</div>
            <div className="grid grid-cols-2 gap-0.5">
              {group.items.map(item => {
                const Icon = item.icon
                const active = activeView === item.id
                return (
                  <button
                    key={item.id}
                    onClick={() => onViewChange(item.id)}
                    className={`flex items-center gap-1 px-1.5 py-1 rounded text-[9px] font-mono transition-colors ${
                      active ? 'bg-obs-border text-obs-text font-semibold' : 'text-obs-dtext hover:text-obs-mtext hover:bg-obs-muted/30'
                    }`}
                  >
                    <Icon size={9} className={active ? 'text-obs-brody' : ''} />
                    {item.label}
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {/* New session */}
      <div className="px-3 py-2 border-b border-obs-border">
        <button onClick={onNewSession} className="w-full flex items-center gap-2 px-2 py-1.5 rounded border border-obs-border/60 text-obs-mtext hover:text-obs-text hover:border-obs-border transition-colors text-xs font-mono">
          <Plus size={11} /> Nouvelle Session
        </button>
      </div>

      {/* Sessions with popover */}
      <div className="px-3 pt-2 flex-1 overflow-y-auto min-h-0">
        <div className="text-[8px] font-mono text-obs-dtext uppercase tracking-wider mb-1.5 flex items-center gap-1">
          <MessageSquare size={8} /> Sessions ({(sessions.length || getSessions().length)})
        </div>
        <div className="space-y-0.5">
          {(sessions.length > 0 ? sessions : getSessions()).map(s => {
            const active = s.id === activeSessionId
            return (
              <div key={s.id} className="group relative">
                <div
                  onClick={() => onSelectSession(s.id)}
                  className={`flex items-start justify-between px-2 py-1.5 rounded cursor-pointer text-[9px] font-mono transition-colors ${
                    active ? 'bg-obs-border/60 text-obs-text' : 'text-obs-mtext hover:text-obs-text hover:bg-obs-muted/40'
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1 mb-0.5">
                      <span className={`shrink-0 text-[8px] px-0.5 py-px rounded ${
                        s.language === 'fr' ? 'bg-obs-memory/20 text-obs-memory' : 'bg-obs-brody/20 text-obs-brody'
                      }`}>{s.language.toUpperCase()}</span>
                      <span className="truncate">{s.preview}</span>
                    </div>
                    <div className="text-obs-dtext text-[8px]">
                      {new Date(s.lastMessageAt).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                  <button onClick={e => handleDelete(e, s.id)} className="shrink-0 ml-1 opacity-0 group-hover:opacity-50 hover:!opacity-100 text-obs-block transition-opacity">
                    <Trash2 size={9} />
                  </button>
                </div>
                <SessionPopover s={s} />
              </div>
            )
          })}
        </div>
      </div>

      {/* Memory sources */}
      <div className="px-3 pt-3 border-t border-obs-border">
        <div className="text-[8px] font-mono text-obs-dtext uppercase tracking-wider mb-1.5 flex items-center gap-1">
          <Database size={8} /> Memory Sources
        </div>
        <div className="space-y-0.5">
          {MEMORY_SOURCES.map(src => (
            <div key={src.id} className="flex items-center justify-between px-2 py-1 rounded">
              <div className="flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${src.active ? 'bg-obs-pass' : 'bg-obs-dtext'}`} />
                <span className="text-[9px] font-mono text-obs-mtext">{src.label}</span>
              </div>
              <span className="text-[8px] font-mono text-obs-memory font-semibold">READONLY</span>
            </div>
          ))}
        </div>
      </div>

      {/* Sovereignty invariants */}
      <div className="px-3 pt-2 pb-3 border-t border-obs-border">
        <div className="text-[8px] font-mono text-obs-dtext uppercase tracking-wider mb-1.5">Sovereignty</div>
        <div className="flex flex-wrap gap-0.5">
          {NON_SOVEREIGNTY_BADGES.map(b => (
            <span key={b.label} className={`${BADGE_CLS[b.color] ?? 'obs-badge-muted'} text-[8px] py-0.5`}>
              {b.label}
            </span>
          ))}
        </div>
      </div>
    </aside>
  )
}
