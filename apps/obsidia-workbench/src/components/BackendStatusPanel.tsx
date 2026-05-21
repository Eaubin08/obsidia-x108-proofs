import { useState, useEffect, useCallback } from 'react'
import { RefreshCw, Wifi } from 'lucide-react'
import { config, getBackendHealth, getGraphitiStatus, getGraphitiReadiness } from '../api/obsidiaClient'

type OnlineStatus = 'ONLINE' | 'OFFLINE' | 'MOCK' | 'CHECKING'

interface StatusState {
  backend: OnlineStatus
  graphiti: OnlineStatus
  apiBase: string
  lastSync: string
  version: string
  entityCount: number
  readinessWarnings: string[]
  engineApi: OnlineStatus
}

const INIT: StatusState = {
  backend:           'CHECKING',
  graphiti:          'CHECKING',
  apiBase:           config.API_BASE,
  lastSync:          '—',
  version:           '—',
  entityCount:       0,
  readinessWarnings: [],
  engineApi:         'CHECKING',
}

function StatusDot({ s }: { s: OnlineStatus }) {
  const cls = {
    ONLINE:   'bg-obs-pass',
    OFFLINE:  'bg-obs-block',
    MOCK:     'bg-obs-hold',
    CHECKING: 'bg-obs-dtext animate-pulse',
  }[s]
  return <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${cls}`} />
}

function StatusBadge({ s }: { s: OnlineStatus }) {
  const cls = {
    ONLINE:   'obs-badge-pass',
    OFFLINE:  'obs-badge-block',
    MOCK:     'obs-badge-hold',
    CHECKING: 'obs-badge-muted',
  }[s]
  return <span className={cls}>{s}</span>
}

function KVRow({ k, v, vClass }: { k: string; v: string; vClass?: string }) {
  return (
    <div className="flex items-center gap-2 py-0.5">
      <span className="text-obs-dtext font-mono text-[10px] w-32 shrink-0">{k}</span>
      <span className={`font-mono text-[10px] ${vClass ?? 'text-obs-mtext'}`}>{v}</span>
    </div>
  )
}

export function BackendStatusPanel() {
  const [st, setSt] = useState<StatusState>(INIT)
  const [loading, setLoading] = useState(false)

  const probe = useCallback(async () => {
    setLoading(true)
    try {
      const [health, graphiti, readiness] = await Promise.all([
        getBackendHealth(),
        getGraphitiStatus(),
        getGraphitiReadiness(),
      ])

      setSt({
        backend:           health.source === 'api' ? (health.data.status === 'healthy' ? 'ONLINE' : 'OFFLINE') : 'MOCK',
        graphiti:          graphiti.source === 'api' ? (graphiti.data.status === 'healthy' ? 'ONLINE' : 'OFFLINE') : 'MOCK',
        apiBase:           config.API_BASE,
        lastSync:          new Date().toLocaleTimeString(),
        version:           health.data.version,
        entityCount:       graphiti.data.entity_count ?? 0,
        readinessWarnings: readiness.data.warnings,
        engineApi:         'CHECKING',
      })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { probe() }, [probe])

  const invariants = [
    { label: 'Brody readonly',          value: 'true',        ok: true },
    { label: 'Memory auto-promo',        value: 'false',       ok: true },
    { label: 'Graphiti write',           value: 'false',       ok: true },
    { label: 'WorldAction dry-run',      value: 'true',        ok: true },
    { label: 'Real chain action',        value: 'false',       ok: true },
    { label: 'decision_authority',       value: 'KX108_ONLY',  ok: true },
  ]

  return (
    <div className="space-y-4">

      {/* Backend status card */}
      <div className="obs-card p-3">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Wifi size={11} className={st.backend === 'ONLINE' ? 'text-obs-pass' : 'text-obs-dtext'} />
            <span className="text-obs-text text-xs font-mono font-semibold">ObsidiaShell</span>
          </div>
          <div className="flex items-center gap-1.5">
            <StatusBadge s={st.backend} />
            <button
              onClick={probe}
              disabled={loading}
              className="p-0.5 rounded text-obs-dtext hover:text-obs-text transition-colors disabled:opacity-50"
            >
              <RefreshCw size={10} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>

        <KVRow k="API base"  v={st.apiBase} />
        <KVRow k="version"   v={st.version} />
        <KVRow k="last sync" v={st.lastSync} />
        <KVRow k="mock fallback" v={String(config.USE_MOCK)} vClass={config.USE_MOCK ? 'text-obs-hold' : 'text-obs-pass'} />
      </div>

      {/* Services */}
      <div>
        <div className="obs-section-header mb-2">Services</div>
        <div className="space-y-1.5">
          {[
            { label: 'ObsidiaShell API (8011)', s: st.backend },
            { label: 'Graphiti V20 frozen',      s: st.graphiti },
            { label: 'Engine API (8000)',          s: st.engineApi },
          ].map(row => (
            <div key={row.label} className="flex items-center justify-between px-2 py-1.5 rounded bg-obs-muted/20">
              <div className="flex items-center gap-2">
                <StatusDot s={row.s} />
                <span className="text-obs-mtext text-[10px] font-mono">{row.label}</span>
              </div>
              <StatusBadge s={row.s} />
            </div>
          ))}
        </div>
      </div>

      {/* Graphiti metrics */}
      {st.backend === 'ONLINE' && (
        <div>
          <div className="obs-section-header mb-2">Graphiti V20 Metrics</div>
          <div className="obs-card p-3 space-y-0.5">
            <KVRow k="entities"   v={String(st.entityCount)} vClass="text-obs-memory" />
            <KVRow k="frozen"     v="true"                   vClass="text-obs-pass" />
            <KVRow k="neo4j_write" v="false"                 vClass="text-obs-block" />
          </div>
          {st.readinessWarnings.length > 0 && (
            <div className="mt-2 space-y-1">
              {st.readinessWarnings.map((w, i) => (
                <div key={i} className="px-2 py-1 rounded bg-obs-hold/5 border border-obs-hold/20 text-[9px] font-mono text-obs-hold">
                  ⚠ {w}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Sovereignty invariants */}
      <div>
        <div className="obs-section-header mb-2">Sovereignty Invariants</div>
        <div className="obs-card p-3 space-y-0.5">
          {invariants.map(inv => (
            <div key={inv.label} className="flex items-center justify-between py-0.5">
              <span className="text-obs-dtext text-[10px] font-mono">{inv.label}</span>
              <span className={`font-mono text-[10px] font-semibold ${inv.ok ? 'text-obs-pass' : 'text-obs-block'}`}>
                {inv.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Start backend hint */}
      {st.backend !== 'ONLINE' && (
        <div className="obs-card p-3 border-obs-hold/30 bg-obs-hold/5">
          <div className="text-[9px] font-mono text-obs-hold font-bold mb-1.5">Start ObsidiaShell backend:</div>
          <div className="text-[9px] font-mono text-obs-mtext space-y-0.5">
            <div>cd obsidiashell-main</div>
            <div>.venv_api8011\Scripts\uvicorn \</div>
            <div className="pl-2">obsidia_core.agent_bridge:app \</div>
            <div className="pl-2">--host 127.0.0.1 --port 8011</div>
          </div>
          <div className="mt-2 text-[9px] font-mono text-obs-dtext">
            Mock fallback is active — UI works without backend.
          </div>
        </div>
      )}

    </div>
  )
}
