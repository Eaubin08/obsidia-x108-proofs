import { useState, useEffect } from 'react'
import { ClipboardList, RefreshCw } from 'lucide-react'
import { getAuditEvents } from '../api/obsidiaClient'
import type { AuditEvent } from '../types/obsidia'
import { MOCK_AUDIT } from '../data/mockData'

const TYPE_COLOR: Record<string, string> = {
  context_read:     'text-obs-memory',
  brody_response:   'text-obs-brody',
  memory_candidate: 'text-obs-memory',
  governance_check: 'text-obs-kernel',
  world_call:       'text-obs-world',
  gencoin_entry:    'text-obs-gencoin',
}

const RESULT_CLASS: Record<string, string> = {
  OK:      'obs-badge-pass',
  BLOCKED: 'obs-badge-block',
  DRY_RUN: 'obs-badge-hold',
  HOLD:    'obs-badge-hold',
}

export function AuditView() {
  const [events, setEvents] = useState<AuditEvent[]>(MOCK_AUDIT)
  const [src, setSrc] = useState<'api' | 'mock'>('mock')
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const r = await getAuditEvents()
      setEvents(r.data)
      setSrc(r.source)
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="flex items-center gap-2">
        <ClipboardList size={13} className="text-obs-mtext" />
        <span className="text-obs-text font-mono text-sm font-semibold">Audit Trail</span>
        <span className={`ml-auto text-[9px] font-mono px-1.5 py-0.5 rounded ${src === 'api' ? 'text-obs-pass bg-obs-pass/10' : 'text-obs-hold bg-obs-hold/10'}`}>
          {src.toUpperCase()}
        </span>
        <button onClick={load} disabled={loading} className="p-1 text-obs-dtext hover:text-obs-text transition-colors disabled:opacity-50">
          <RefreshCw size={10} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      <div className="rounded-lg border border-obs-border p-2.5 text-[9px] font-mono text-obs-dtext">
        Append-only audit trail · WorldActionBus · Read-only replay · No deletion
      </div>

      <div className="space-y-0.5">
        {events.map(ev => (
          <div key={ev.event_id} className="flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-obs-muted/20 transition-colors">
            <span className={`text-[9px] font-mono w-28 shrink-0 ${TYPE_COLOR[ev.type] ?? 'text-obs-mtext'}`}>
              {ev.type}
            </span>
            <span className="text-obs-mtext text-[10px] font-mono flex-1 truncate">{ev.description}</span>
            <span className={`shrink-0 text-[9px] font-mono ${RESULT_CLASS[ev.result] ?? 'obs-badge-muted'}`}>
              {ev.result}
            </span>
            <span className="text-obs-dtext text-[9px] font-mono shrink-0">
              {new Date(ev.timestamp).toLocaleTimeString()}
            </span>
          </div>
        ))}
      </div>

      {events.length === 0 && (
        <div className="text-center text-obs-dtext text-[10px] font-mono py-8">No audit events yet.</div>
      )}
    </div>
  )
}
