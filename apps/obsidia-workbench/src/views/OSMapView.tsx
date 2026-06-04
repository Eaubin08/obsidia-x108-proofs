// src/views/OSMapView.tsx
// P38 — Full OS Map Workbench View
// Affiche la carte complète du chemin moteur choisi par P36/P37.
// POST /api/runtime-wiring/os-map/query → detected_intents, capabilities, path, fonctions, tests, docs, evidence.
// NO ACT. NO write. KX108_ONLY. READONLY_PREVIEW_ONLY.

import { useState, useCallback } from 'react'
import {
  Map, Shield, Lock, RefreshCw, Search, XCircle,
  CheckCircle, Cpu, FileCode, BookOpen, Layers,
} from 'lucide-react'

const ENGINE_BASE = (
  (import.meta.env.VITE_ENGINE_API_BASE as string | undefined)
  ?? 'http://127.0.0.1:8000'
).replace(/\/$/, '')

const OS_MAP_QUERY_URL = `${ENGINE_BASE}/api/runtime-wiring/os-map/query`
const OS_MAP_STATUS_URL = `${ENGINE_BASE}/api/runtime-wiring/os-map/status`

// ── Types ──────────────────────────────────────────────────────────────────────

interface SelectedPath {
  path_id?: string
  capability_chain?: string[]
  modules?: string[]
  adapters?: string[]
  routes?: string[]
  source_families?: string[]
  source_subfamilies?: string[]
  evidence_packs?: string[]
  x108_decision?: string
  score?: number
  reason?: string
  runtime_allowed_now?: boolean
  emits_act?: boolean
  decision_authority?: string
  selected_functions?: string[]
  selected_classes?: string[]
  selected_routes?: string[]
  selected_tests?: string[]
  selected_docs?: string[]
  inventory_linked?: boolean
  coverage_status?: string
}

interface HydrationPlan {
  planned_files?: string[]
  planned_files_count?: number
  max_files?: number
  estimated_bytes?: number
  readonly?: boolean
  emits_act?: boolean
}

interface OSMapResult {
  os_map_status?: string
  query?: string
  detected_intents?: string[]
  required_capabilities?: string[]
  selected_runtime_path?: SelectedPath
  selected_modules?: string[]
  selected_adapters?: string[]
  selected_routes?: string[]
  selected_source_families?: string[]
  selected_source_subfamilies?: string[]
  selected_evidence_packs?: string[]
  inventory_linked?: boolean
  inventory_status?: string
  selected_functions?: string[]
  selected_classes?: string[]
  selected_routes_inventory?: string[]
  selected_tests?: string[]
  selected_docs?: string[]
  coverage_status?: string
  hydration_plan?: HydrationPlan
  source_file_refs?: string[]
  x108_decision?: string
  action_blocked?: boolean
  readonly?: boolean
  emits_act?: boolean
  decision_authority?: string
  runtime_allowed_now?: boolean
}

type FetchState = 'idle' | 'loading' | 'ok' | 'error'

// ── Sub-components ─────────────────────────────────────────────────────────────

function SectionTitle({ icon: Icon, label, color }: {
  icon: typeof Shield
  label: string
  color?: string
}) {
  return (
    <div className="flex items-center gap-1.5 mb-2">
      <Icon className={`w-3.5 h-3.5 ${color ?? 'text-obs-kernel'}`} />
      <span className={`text-[10px] font-bold tracking-widest uppercase font-mono ${color ?? 'text-obs-kernel'}`}>
        {label}
      </span>
    </div>
  )
}

function Pill({ label, value, accent }: { label: string; value: string | number | undefined | boolean; accent?: string }) {
  const display = value === undefined || value === null ? '—' : String(value)
  return (
    <div className="flex items-center justify-between py-0.5 border-b border-obs-border last:border-0">
      <span className="text-obs-muted text-[10px] font-mono">{label}</span>
      <span className={`text-[10px] font-bold font-mono ${accent ?? 'text-obs-kernel'}`}>{display}</span>
    </div>
  )
}

function Flag({ label, value }: { label: string; value: boolean | undefined }) {
  const isGood = value === false
  return (
    <div className="flex items-center justify-between py-0.5 border-b border-obs-border last:border-0">
      <span className="text-obs-muted text-[10px] font-mono">{label}</span>
      <span className={`text-[10px] font-bold font-mono ${isGood ? 'text-green-400' : 'text-red-400'}`}>
        {String(value ?? '—')}
      </span>
    </div>
  )
}

function ChipList({ items, color }: { items: string[]; color?: string }) {
  if (!items.length) return <span className="text-obs-dtext text-[10px] font-mono">—</span>
  return (
    <div className="flex flex-wrap gap-1">
      {items.map((item) => (
        <span
          key={item}
          className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${color ?? 'border-obs-border bg-obs-border/40 text-obs-proof'}`}
        >
          {item}
        </span>
      ))}
    </div>
  )
}

function PathCard({ path }: { path: SelectedPath }) {
  const isBlocked = path.capability_chain?.includes('ACTION_REQUEST_BLOCKED')
  return (
    <div className={`rounded border p-2 ${isBlocked ? 'border-red-700 bg-red-900/10' : 'border-obs-border bg-obs-bg'}`}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-[9px] font-mono text-obs-dtext">{path.path_id ?? '—'}</span>
        {path.score !== undefined && (
          <span className="text-[9px] font-mono text-obs-kernel font-bold">score: {path.score}</span>
        )}
      </div>
      {path.capability_chain && (
        <div className="mb-1.5">
          <span className="text-[9px] font-mono text-obs-muted mr-1">capabilities:</span>
          <ChipList items={path.capability_chain} color={isBlocked ? 'border-red-700 bg-red-900/20 text-red-300' : undefined} />
        </div>
      )}
      {path.modules && path.modules.length > 0 && (
        <div className="mb-1">
          <span className="text-[9px] font-mono text-obs-muted block mb-0.5">modules:</span>
          <ChipList items={path.modules} color="border-obs-border/60 bg-obs-surface text-obs-muted" />
        </div>
      )}
      {path.adapters && path.adapters.length > 0 && (
        <div className="mb-1">
          <span className="text-[9px] font-mono text-obs-muted block mb-0.5">adapters:</span>
          <ChipList items={path.adapters} color="border-obs-proof/40 bg-obs-proof/10 text-obs-proof" />
        </div>
      )}
      {path.reason && (
        <p className="text-[9px] font-mono text-obs-dtext mt-1 italic">{path.reason}</p>
      )}
      <div className="mt-1.5 flex items-center gap-2">
        <span className={`text-[8px] font-mono px-1 rounded ${path.x108_decision === 'ALLOW_CONTEXT_ONLY' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
          {path.x108_decision ?? '—'}
        </span>
        <span className="text-[8px] font-mono text-obs-dtext">
          {path.runtime_allowed_now ? '⚠ runtime_allowed_now=TRUE' : '✓ runtime_allowed_now=false'}
        </span>
      </div>
    </div>
  )
}

// ── Main View ─────────────────────────────────────────────────────────────────

export function OSMapView() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<OSMapResult | null>(null)
  const [fetchState, setFetchState] = useState<FetchState>('idle')
  const [error, setError] = useState<string | null>(null)

  const runQuery = useCallback(async () => {
    if (!query.trim()) return
    setFetchState('loading')
    setError(null)
    setResult(null)
    try {
      const res = await fetch(OS_MAP_QUERY_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim(), max_paths: 5 }),
        signal: AbortSignal.timeout(30000),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json: OSMapResult = await res.json()
      setResult(json)
      setFetchState('ok')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
      setFetchState('error')
    }
  }, [query])

  const isBlocked = result?.action_blocked === true
  const isReady = result?.os_map_status === 'OS_MAP_READY' || result?.os_map_status === 'ACTION_BLOCKED'

  return (
    <div className="flex-1 overflow-y-auto p-4 bg-obs-bg text-obs-text">

      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <Map className="w-4 h-4 text-obs-kernel" />
        <h1 className="text-xs font-bold tracking-widest uppercase text-obs-kernel">
          OS Map — Full Engine Path
        </h1>
        <span className="ml-auto text-[10px] text-obs-muted font-mono">P38 · KX108_ONLY · READONLY</span>
      </div>

      {/* Invariants notice */}
      <div className="mb-3 px-3 py-1.5 rounded border border-yellow-700 bg-yellow-900/20 text-yellow-300 text-[10px] font-mono flex items-center gap-2">
        <Lock className="w-3 h-3 shrink-0" />
        No ACT · No write · No runtime_allowed_now · No Graphiti write · KX108_ONLY
      </div>

      {/* Query panel */}
      <div className="mb-4 bg-obs-surface border border-obs-border rounded p-3">
        <SectionTitle icon={Search} label="Query" color="text-obs-muted" />
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && runQuery()}
            placeholder="ex: IR alphabet reverse OS · 34 arbres agents · envoie un mail…"
            className="flex-1 text-[10px] font-mono bg-obs-bg border border-obs-border rounded px-2 py-1.5 text-obs-text placeholder-obs-muted outline-none focus:border-obs-kernel"
          />
          <button
            onClick={runQuery}
            disabled={fetchState === 'loading' || !query.trim()}
            className="text-[10px] font-mono px-3 py-1 rounded bg-obs-kernel text-obs-bg hover:opacity-80 disabled:opacity-40 transition flex items-center gap-1"
          >
            {fetchState === 'loading'
              ? <><RefreshCw className="w-3 h-3 animate-spin" /> …</>
              : <><Map className="w-3 h-3" /> Show OS Map</>
            }
          </button>
        </div>
        {fetchState === 'error' && (
          <p className="mt-2 text-red-400 text-[10px] font-mono">Erreur : {error}</p>
        )}
      </div>

      {/* Results */}
      {result && isReady && (
        <div className="grid grid-cols-1 gap-3 max-w-2xl">

          {/* ACTION BLOCKED banner */}
          {isBlocked && (
            <div className="flex items-center gap-2 px-3 py-2 rounded border border-red-700 bg-red-900/20 text-red-300 text-xs font-mono">
              <XCircle className="w-4 h-4 shrink-0" />
              <div>
                <div className="font-bold">ACTION_REQUEST_BLOCKED</div>
                <div className="text-[10px] opacity-80 mt-0.5">
                  Requête d'action détectée. Le moteur est en mode READONLY. Aucune exécution.
                </div>
              </div>
            </div>
          )}

          {/* 1 — Intents + Capabilities */}
          <div className="bg-obs-surface border border-obs-border rounded p-3">
            <SectionTitle icon={Layers} label="P36 — Intent & Capability Router" color="text-obs-proof" />
            <div className="mb-2">
              <span className="text-[9px] font-mono text-obs-muted block mb-1">detected_intents</span>
              <ChipList
                items={result.detected_intents ?? []}
                color="border-obs-kernel/40 bg-obs-kernel/10 text-obs-kernel"
              />
            </div>
            <div>
              <span className="text-[9px] font-mono text-obs-muted block mb-1">required_capabilities</span>
              <ChipList
                items={result.required_capabilities ?? []}
                color={isBlocked
                  ? 'border-red-700 bg-red-900/20 text-red-300'
                  : 'border-obs-proof/40 bg-obs-proof/10 text-obs-proof'
                }
              />
            </div>
          </div>

          {/* 2 — Selected Runtime Path */}
          {result.selected_runtime_path && (
            <div className="bg-obs-surface border border-obs-border rounded p-3">
              <SectionTitle icon={Cpu} label="Selected Runtime Path" color="text-obs-kernel" />
              <PathCard path={result.selected_runtime_path} />
              <div className="mt-2 grid grid-cols-1 gap-0.5">
                <Pill label="source_families" value={(result.selected_source_families ?? []).join(', ') || '—'} accent="text-obs-proof" />
                <Pill label="source_subfamilies" value={(result.selected_source_subfamilies ?? []).join(', ') || '—'} accent="text-obs-proof" />
                <Pill label="evidence_packs" value={(result.selected_evidence_packs ?? []).join(', ') || '—'} accent="text-obs-proof" />
              </div>
            </div>
          )}

          {/* 3 — Runtime Inventory (P37) */}
          <div className="bg-obs-surface border border-obs-border rounded p-3">
            <SectionTitle icon={FileCode} label="P37 — Runtime Inventory" color="text-obs-brody" />
            <Pill
              label="inventory_status"
              value={result.inventory_status}
              accent={result.inventory_linked ? 'text-green-400' : 'text-yellow-400'}
            />
            <Pill label="coverage_status" value={result.coverage_status} accent="text-obs-kernel" />

            <div className="mt-2 space-y-1.5">
              {(result.selected_functions ?? []).length > 0 && (
                <div>
                  <span className="text-[9px] font-mono text-obs-muted block mb-0.5">selected_functions</span>
                  <ChipList
                    items={result.selected_functions ?? []}
                    color="border-obs-brody/40 bg-obs-brody/10 text-obs-brody"
                  />
                </div>
              )}
              {(result.selected_classes ?? []).length > 0 && (
                <div>
                  <span className="text-[9px] font-mono text-obs-muted block mb-0.5">selected_classes</span>
                  <ChipList items={result.selected_classes ?? []} color="border-obs-border bg-obs-surface text-obs-muted" />
                </div>
              )}
              {(result.selected_routes_inventory ?? []).length > 0 && (
                <div>
                  <span className="text-[9px] font-mono text-obs-muted block mb-0.5">selected_routes (inventory)</span>
                  <ChipList
                    items={result.selected_routes_inventory ?? []}
                    color="border-obs-kernel/40 bg-obs-kernel/10 text-obs-kernel"
                  />
                </div>
              )}
              {(result.selected_tests ?? []).length > 0 && (
                <div>
                  <span className="text-[9px] font-mono text-obs-muted block mb-0.5">selected_tests</span>
                  <ChipList items={result.selected_tests ?? []} color="border-green-700/40 bg-green-900/10 text-green-400" />
                </div>
              )}
              {(result.selected_docs ?? []).length > 0 && (
                <div>
                  <span className="text-[9px] font-mono text-obs-muted block mb-0.5">selected_docs</span>
                  <ChipList items={result.selected_docs ?? []} color="border-obs-memory/40 bg-obs-memory/10 text-obs-memory" />
                </div>
              )}
            </div>
          </div>

          {/* 4 — Hydration Plan */}
          {result.hydration_plan && (
            <div className="bg-obs-surface border border-obs-border rounded p-3">
              <SectionTitle icon={BookOpen} label="Hydration Plan" color="text-obs-muted" />
              <Pill label="planned_files_count" value={result.hydration_plan.planned_files_count} accent="text-obs-proof" />
              <Pill label="max_files" value={result.hydration_plan.max_files} accent="text-obs-muted" />
              <Pill label="estimated_bytes" value={result.hydration_plan.estimated_bytes} accent="text-obs-muted" />
              <Flag label="emits_act" value={result.hydration_plan.emits_act} />
              {(result.source_file_refs ?? []).length > 0 && (
                <div className="mt-1.5">
                  <span className="text-[9px] font-mono text-obs-muted block mb-0.5">source_file_refs</span>
                  <ChipList items={result.source_file_refs ?? []} color="border-obs-border bg-obs-bg text-obs-dtext" />
                </div>
              )}
            </div>
          )}

          {/* 5 — X108 Boundary */}
          <div className="bg-obs-surface border border-obs-border rounded p-3">
            <SectionTitle icon={Shield} label="X108 Boundary" color="text-obs-kernel" />
            <Pill
              label="x108_decision"
              value={result.x108_decision}
              accent={
                result.x108_decision === 'ALLOW_CONTEXT_ONLY' ? 'text-green-400'
                : result.x108_decision === 'BLOCK_OR_HOLD_CONTEXT_ONLY' ? 'text-red-400'
                : 'text-yellow-400'
              }
            />
            <Pill label="decision_authority" value={result.decision_authority} accent="text-obs-kernel" />
            <Flag label="runtime_allowed_now" value={result.runtime_allowed_now} />
            <Flag label="emits_act" value={result.emits_act} />
            <Flag label="readonly — must be true" value={!result.readonly} />
            <Flag label="memory_write" value={(result as Record<string, boolean>).memory_write} />
            <Flag label="graph_write" value={(result as Record<string, boolean>).graph_write} />
            <Flag label="kernel_mutation" value={(result as Record<string, boolean>).kernel_mutation} />
          </div>

          {/* OS Map status */}
          <div className="flex items-center gap-2 px-3 py-2 rounded border border-obs-border bg-obs-surface">
            {isBlocked
              ? <XCircle className="w-3.5 h-3.5 text-red-400" />
              : <CheckCircle className="w-3.5 h-3.5 text-green-400" />
            }
            <span className="text-[10px] font-mono text-obs-muted">
              os_map_status: <span className={`font-bold ${isBlocked ? 'text-red-400' : 'text-green-400'}`}>
                {result.os_map_status}
              </span>
            </span>
          </div>

        </div>
      )}

      {/* Idle state */}
      {fetchState === 'idle' && (
        <div className="max-w-2xl mt-2">
          <div className="px-3 py-3 rounded border border-obs-border bg-obs-surface text-obs-muted text-[10px] font-mono space-y-1">
            <div className="font-bold text-obs-text mb-1">Exemples de requêtes :</div>
            {[
              'IR alphabet reverse OS interlanguage canon',
              '34 arbres agents registry',
              'lois protocoles non décision boundary',
              'RSSI sécurité audit conformité',
              'mémoire Brody Graphiti réintégration',
              'envoie un mail à l\'équipe',
            ].map((ex) => (
              <button
                key={ex}
                onClick={() => { setQuery(ex); }}
                className="block text-obs-brody hover:underline text-left"
              >
                → {ex}
              </button>
            ))}
          </div>
        </div>
      )}

    </div>
  )
}
