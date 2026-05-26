import { useState, useEffect } from 'react'
import { Search, RefreshCw, Lock } from 'lucide-react'
import { getGraphitiStatus, getGraphitiMetrics, getGraphitiReadiness, getContextPacket } from '../api/obsidiaClient'

export function GraphitiView() {
  const [query, setQuery] = useState('governance')
  const [results, setResults] = useState<string[]>([])
  const [resultSrc, setResultSrc] = useState<'api' | 'mock'>('mock')
  const [status, setStatus] = useState<{ status: string; frozen: boolean; entity_count: number; run_id: string } | null>(null)
  const [metrics, setMetrics] = useState<{ entity_count: number; relation_count: number; episode_count: number; version: string } | null>(null)
  const [warnings, setWarnings] = useState<string[]>([])
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    Promise.all([getGraphitiStatus(), getGraphitiMetrics(), getGraphitiReadiness()]).then(([s, m, r]) => {
      setStatus({ status: s.data.status, frozen: s.data.frozen, entity_count: s.data.entity_count ?? 0, run_id: s.data.run_id ?? 'mock' })
      setMetrics({ entity_count: m.data.entity_count, relation_count: m.data.relation_count, episode_count: m.data.episode_count, version: m.data.version ?? 'v20' })
      setWarnings(r.data.warnings)
    })
    handleSearch('governance')
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSearch = async (q?: string) => {
    const qStr = (q ?? query).trim()
    if (!qStr) return
    setSearching(true)
    try {
      const r = await getContextPacket(qStr)
      setResults(r.data.context_items)
      setResultSrc(r.source)
    } finally { setSearching(false) }
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Search size={13} className="text-obs-memory" />
        <span className="text-obs-text font-mono text-sm font-semibold">Graphiti V20 — Frozen Readonly</span>
        <span className="ml-auto text-[9px] font-mono px-1.5 py-0.5 rounded text-obs-pass bg-obs-pass/10">READONLY</span>
      </div>

      {/* Invariants */}
      <div className="rounded-lg border border-obs-block/20 bg-obs-block/5 p-2.5 flex gap-4 text-[9px] font-mono">
        <span className="text-obs-mtext">neo4j_write=<span className="text-obs-block">false</span></span>
        <span className="text-obs-mtext">graphiti_write=<span className="text-obs-block">false</span></span>
        <span className="text-obs-mtext">live_neo4j_dependency=<span className="text-obs-block">false</span></span>
        <span className="text-obs-mtext">kernel_decision=<span className="text-obs-dtext">NONE</span></span>
      </div>

      {/* Search */}
      <div className="flex gap-2">
        <div className="flex-1 bg-obs-surface border border-obs-border rounded-lg flex items-center gap-2 px-3 focus-within:border-obs-memory/50 transition-colors">
          <Search size={10} className="text-obs-dtext shrink-0" />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleSearch() }}
            className="flex-1 bg-transparent text-obs-text text-xs font-mono py-2 outline-none placeholder:text-obs-dtext"
            placeholder="Query frozen Graphiti context..."
          />
        </div>
        <button
          onClick={() => handleSearch()}
          disabled={searching}
          className="px-3 py-2 rounded-lg bg-obs-memory/20 border border-obs-memory/30 text-obs-memory text-xs font-mono font-semibold hover:bg-obs-memory/30 disabled:opacity-50 transition-colors"
        >
          {searching ? <RefreshCw size={11} className="animate-spin" /> : 'SEARCH'}
        </button>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="text-obs-dtext text-[10px] font-mono font-semibold uppercase tracking-wider">
              Context Results ({results.length})
            </div>
            <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded ${resultSrc === 'api' ? 'text-obs-pass bg-obs-pass/10' : 'text-obs-hold bg-obs-hold/10'}`}>
              {resultSrc === 'api' ? 'LIVE_GRAPHITI_V20' : 'MOCK_FALLBACK'}
            </span>
          </div>
          <div className="space-y-1">
            {results.map((r, i) => (
              <div key={i} className="flex gap-2 px-3 py-2 rounded-lg bg-obs-surface border border-obs-border">
                <span className="text-obs-dtext text-[10px] font-mono shrink-0">{i + 1}.</span>
                <span className="text-obs-mtext text-[10px] font-mono">{r}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Status + metrics */}
      {status && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-1.5 uppercase tracking-wider">Status</div>
            <div className="bg-obs-surface border border-obs-border rounded-lg p-3 text-[10px] font-mono space-y-0.5">
              <div className="flex justify-between"><span className="text-obs-dtext">status</span><span className="text-obs-pass">{status.status}</span></div>
              <div className="flex justify-between"><span className="text-obs-dtext">frozen</span><span className="text-obs-pass">{String(status.frozen)}</span></div>
              <div className="flex justify-between"><span className="text-obs-dtext">entities</span><span className="text-obs-memory">{status.entity_count}</span></div>
              <div className="flex justify-between"><span className="text-obs-dtext">run_id</span><span className="text-obs-mtext truncate ml-2">{status.run_id.slice(0, 18)}</span></div>
            </div>
          </div>
          {metrics && (
            <div>
              <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-1.5 uppercase tracking-wider">Metrics</div>
              <div className="bg-obs-surface border border-obs-border rounded-lg p-3 text-[10px] font-mono space-y-0.5">
                <div className="flex justify-between"><span className="text-obs-dtext">entities</span><span className="text-obs-memory">{metrics.entity_count}</span></div>
                <div className="flex justify-between"><span className="text-obs-dtext">relations</span><span className="text-obs-memory">{metrics.relation_count}</span></div>
                <div className="flex justify-between"><span className="text-obs-dtext">episodes</span><span className="text-obs-memory">{metrics.episode_count}</span></div>
                <div className="flex justify-between"><span className="text-obs-dtext">version</span><span className="text-obs-mtext">{metrics.version}</span></div>
              </div>
            </div>
          )}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="space-y-1">
          {warnings.map((w, i) => (
            <div key={i} className="px-3 py-1.5 rounded-lg bg-obs-hold/5 border border-obs-hold/20 text-[9px] font-mono text-obs-hold">
              ⚠ {w}
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center gap-1 text-[9px] font-mono text-obs-dtext">
        <Lock size={9} />
        Graphiti V20 frozen context — read-only queries only
      </div>
    </div>
  )
}
