// src/views/RuntimeWiringPreviewView.tsx
// P11A — Runtime Wiring Preview View
// Fetches GET /api/runtime-wiring/preview and displays dry-run state.
// NO ACT. NO runtime activation. KX108_ONLY. READONLY_PREVIEW_ONLY.

import { useState, useEffect, useCallback } from 'react'
import { Shield, RefreshCw, Lock, Database, CheckCircle, XCircle } from 'lucide-react'

const ENGINE_BASE = (
  (import.meta.env.VITE_ENGINE_API_BASE as string | undefined)
  ?? 'http://127.0.0.1:8000'
).replace(/\/$/, '')

const PREVIEW_URL = `${ENGINE_BASE}/api/runtime-wiring/preview`

// Expected decisions — used for display validation (never emitted as actions)
const EXPECTED_CONTEXT_ONLY  = 'ALLOW_CONTEXT_ONLY'
const EXPECTED_CRITICAL       = 'HOLD'

interface PreviewPayload {
  status?: string
  runtime_active?: boolean
  decision_authority?: string
  context_only_decision?: string
  critical_action_decision?: string
  emits_act?: boolean
  proof_claim?: boolean
  source_registry_entries?: number
  families_sampled?: number
  context_packets_count?: number
  dry_run?: boolean
  safety?: {
    zip_extraction?: boolean
    source_pack_import?: boolean
    runtime_active?: boolean
    world_action?: boolean
    memory_write?: boolean
    graph_write?: boolean
    packages_created?: boolean
  }
}

type FetchState = 'idle' | 'loading' | 'ok' | 'error'

function Flag({ label, value }: { label: string; value: boolean | undefined }) {
  const isGood = value === false
  return (
    <div className="flex items-center justify-between py-1 border-b border-obs-border last:border-0">
      <span className="text-obs-muted text-xs font-mono">{label}</span>
      <span className={`text-xs font-bold font-mono ${isGood ? 'text-green-400' : 'text-red-400'}`}>
        {String(value ?? '—')}
      </span>
    </div>
  )
}

function Pill({ label, value, accent }: { label: string; value: string | number | undefined; accent?: string }) {
  return (
    <div className="flex items-center justify-between py-1 border-b border-obs-border last:border-0">
      <span className="text-obs-muted text-xs font-mono">{label}</span>
      <span className={`text-xs font-bold font-mono ${accent ?? 'text-obs-kernel'}`}>{String(value ?? '—')}</span>
    </div>
  )
}

export function RuntimeWiringPreviewView() {
  const [data, setData] = useState<PreviewPayload | null>(null)
  const [state, setState] = useState<FetchState>('idle')
  const [error, setError] = useState<string | null>(null)
  const [ts, setTs] = useState<string>('')

  const load = useCallback(async () => {
    setState('loading')
    setError(null)
    try {
      const res = await fetch(PREVIEW_URL, { signal: AbortSignal.timeout(30000) })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json: PreviewPayload = await res.json()
      setData(json)
      setState('ok')
      setTs(new Date().toISOString())
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
      setState('error')
    }
  }, [])

  useEffect(() => { load() }, [load])

  return (
    <div className="flex-1 overflow-y-auto p-4 bg-obs-bg text-obs-text">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-5 h-5 text-obs-kernel" />
        <h1 className="text-sm font-bold tracking-widest uppercase text-obs-kernel">
          Runtime Wiring Preview
        </h1>
        <span className="ml-auto text-xs text-obs-muted font-mono">KX108_ONLY</span>
        <button
          onClick={load}
          disabled={state === 'loading'}
          className="p-1 rounded hover:bg-obs-surface text-obs-muted hover:text-obs-text transition"
          title="Refresh"
        >
          <RefreshCw className={`w-4 h-4 ${state === 'loading' ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Notice */}
      <div className="mb-4 px-3 py-2 rounded border border-yellow-700 bg-yellow-900/20 text-yellow-300 text-xs font-mono">
        Preview read-only. No ACT. No runtime activation. Source: {PREVIEW_URL}
      </div>

      {/* Error */}
      {state === 'error' && (
        <div className="mb-4 px-3 py-2 rounded border border-red-700 bg-red-900/20 text-red-300 text-xs font-mono">
          API unreachable: {error}
        </div>
      )}

      {/* Loading */}
      {state === 'loading' && !data && (
        <div className="text-obs-muted text-xs font-mono animate-pulse">Loading registry preview…</div>
      )}

      {data && (
        <div className="grid grid-cols-1 gap-3 max-w-2xl">

          {/* Source Registry */}
          <div className="bg-obs-surface border border-obs-border rounded p-3">
            <div className="flex items-center gap-1 mb-2">
              <Database className="w-4 h-4 text-obs-proof" />
              <span className="text-xs font-bold tracking-widest uppercase text-obs-proof">Source Registry</span>
            </div>
            <Pill label="source_registry_entries" value={data.source_registry_entries} accent="text-obs-proof" />
            <Pill label="families_sampled" value={data.families_sampled} accent="text-obs-proof" />
            <Pill label="context_packets_count" value={data.context_packets_count} accent="text-obs-proof" />
          </div>

          {/* Adapter Routing */}
          <div className="bg-obs-surface border border-obs-border rounded p-3">
            <div className="flex items-center gap-1 mb-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span className="text-xs font-bold tracking-widest uppercase text-green-400">Adapter Routing</span>
            </div>
            <Pill label="status" value={data.status} accent="text-obs-kernel" />
            <Pill label="dry_run" value={String(data.dry_run)} accent="text-green-400" />
          </div>

          {/* X108 Dry-Run Decisions */}
          <div className="bg-obs-surface border border-obs-border rounded p-3">
            <div className="flex items-center gap-1 mb-2">
              <Shield className="w-4 h-4 text-obs-kernel" />
              <span className="text-xs font-bold tracking-widest uppercase text-obs-kernel">X108 Dry-Run Decisions</span>
            </div>
            <Pill label="context_only_decision" value={data.context_only_decision}
              accent={data.context_only_decision === EXPECTED_CONTEXT_ONLY ? 'text-green-400' : 'text-red-400'} />
            <Pill label="critical_action_decision" value={data.critical_action_decision}
              accent={data.critical_action_decision === EXPECTED_CRITICAL ? 'text-yellow-400' : 'text-red-400'} />
            <Pill label="decision_authority" value={data.decision_authority} accent="text-obs-kernel" />
          </div>

          {/* Engine Bridge Preview */}
          <div className="bg-obs-surface border border-obs-border rounded p-3">
            <div className="flex items-center gap-1 mb-2">
              <XCircle className="w-4 h-4 text-obs-block" />
              <span className="text-xs font-bold tracking-widest uppercase text-obs-block">Engine Bridge Preview</span>
            </div>
            <Flag label="runtime_active" value={data.runtime_active} />
            <Flag label="emits_act" value={data.emits_act} />
            <Flag label="proof_claim" value={data.proof_claim} />
          </div>

          {/* Safety Locks */}
          <div className="bg-obs-surface border border-obs-border rounded p-3">
            <div className="flex items-center gap-1 mb-2">
              <Lock className="w-4 h-4 text-obs-kernel" />
              <span className="text-xs font-bold tracking-widest uppercase text-obs-kernel">Safety Locks</span>
            </div>
            <Flag label="zip_extraction" value={data.safety?.zip_extraction} />
            <Flag label="source_pack_import" value={data.safety?.source_pack_import} />
            <Flag label="world_action" value={data.safety?.world_action} />
            <Flag label="memory_write" value={data.safety?.memory_write} />
            <Flag label="graph_write" value={data.safety?.graph_write} />
            <Flag label="packages_created" value={data.safety?.packages_created} />
          </div>

        </div>
      )}

      {ts && (
        <p className="mt-4 text-obs-muted text-xs font-mono">Last fetched: {ts}</p>
      )}
    </div>
  )
}
