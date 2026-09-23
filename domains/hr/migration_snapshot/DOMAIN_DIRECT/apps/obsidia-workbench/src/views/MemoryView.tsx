import { useState, useEffect } from 'react'
import { Database, RefreshCw } from 'lucide-react'
import { getMemoryCandidates } from '../api/obsidiaClient'
import type { MemoryCandidate } from '../types/obsidia'
import { MEMORY_SOURCES } from '../data/mockData'

const STATUS_CLASS: Record<string, string> = {
  CANDIDATE_ONLY:  'obs-badge-memory',
  NEEDS_REVIEW:    'obs-badge-hold',
  PROMOTION_READY: 'obs-badge-proof',
  REJECTED:        'obs-badge-block',
  FROZEN:          'obs-badge-muted',
}

export function MemoryView() {
  const [candidates, setCandidates] = useState<MemoryCandidate[]>([])
  const [src, setSrc] = useState<'api' | 'mock'>('mock')
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const r = await getMemoryCandidates()
      setCandidates(r.data)
      setSrc(r.source)
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Database size={13} className="text-obs-memory" />
          <span className="text-obs-text font-mono text-sm font-semibold">Memory — CANDIDATE_ONLY</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded ${src === 'api' ? 'text-obs-pass bg-obs-pass/10' : 'text-obs-hold bg-obs-hold/10'}`}>
            {src.toUpperCase()}
          </span>
          <button onClick={load} disabled={loading} className="p-1 text-obs-dtext hover:text-obs-text transition-colors disabled:opacity-50">
            <RefreshCw size={10} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Sovereignty invariants */}
      <div className="rounded-lg border border-obs-block/20 bg-obs-block/5 p-3 text-[9px] font-mono space-y-0.5">
        <div className="text-obs-block font-semibold mb-1">MEMORY WRITE CONSTRAINTS</div>
        <div className="text-obs-mtext">memory_write=<span className="text-obs-block">false</span></div>
        <div className="text-obs-mtext">auto_promotion_allowed=<span className="text-obs-block">false</span></div>
        <div className="text-obs-mtext">graphiti_write=<span className="text-obs-block">false</span></div>
        <div className="text-obs-mtext">neo4j_write=<span className="text-obs-block">false</span></div>
        <div className="text-obs-mtext">decision_authority=<span className="text-obs-kernel">KX108_ONLY</span></div>
      </div>

      {/* Memory sources */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Source Registry</div>
        <div className="space-y-1">
          {MEMORY_SOURCES.map(s => (
            <div key={s.id} className="flex items-center justify-between px-3 py-2 rounded-lg bg-obs-surface border border-obs-border">
              <div className="flex items-center gap-2">
                <span className={`w-1.5 h-1.5 rounded-full ${s.active ? 'bg-obs-pass' : 'bg-obs-dtext'}`} />
                <span className="text-obs-text text-[10px] font-mono">{s.label}</span>
              </div>
              <span className="text-obs-memory text-[9px] font-mono font-semibold">READONLY</span>
            </div>
          ))}
        </div>
      </div>

      {/* Candidates */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">
          Candidates ({candidates.length}) — Human Review Required
        </div>
        <div className="space-y-2">
          {candidates.map(c => (
            <div key={c.candidate_id} className="bg-obs-surface border border-obs-border rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-obs-mtext text-[10px] font-mono truncate">{c.candidate_id}</span>
                <span className={STATUS_CLASS[c.status] ?? 'obs-badge-muted'}>{c.status}</span>
              </div>
              <p className="text-obs-mtext text-[10px] font-mono mb-2">{c.content_summary}</p>
              <div className="flex gap-2 flex-wrap text-[9px] font-mono text-obs-dtext">
                <span>source=<span className="text-obs-memory">{c.source_type}</span></span>
                <span>write=<span className="text-obs-block">false</span></span>
                <span>auto_promo=<span className="text-obs-block">false</span></span>
              </div>
              {c.status === 'PROMOTION_READY' && (
                <div className="mt-2 p-1.5 rounded bg-obs-proof/5 border border-obs-proof/20 text-[9px] font-mono text-obs-proof">
                  ⚠ HUMAN REVIEW REQUIRED — no auto-promotion
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Graphiti status */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Graphiti V20</div>
        <div className="bg-obs-surface border border-obs-border rounded-lg p-3 text-[10px] font-mono space-y-0.5">
          <div className="flex justify-between"><span className="text-obs-dtext">mode</span><span className="text-obs-pass">READONLY BRIDGE</span></div>
          <div className="flex justify-between"><span className="text-obs-dtext">neo4j_write</span><span className="text-obs-block">false</span></div>
          <div className="flex justify-between"><span className="text-obs-dtext">graphiti_write</span><span className="text-obs-block">false</span></div>
          <div className="flex justify-between"><span className="text-obs-dtext">decision_authority</span><span className="text-obs-kernel">KX108_ONLY</span></div>
          <div className="flex justify-between"><span className="text-obs-dtext">is_frozen</span><span className="text-obs-pass">true</span></div>
        </div>
      </div>
    </div>
  )
}
