import { useState, useEffect } from 'react'
import { Shield, CheckCircle, RefreshCw } from 'lucide-react'
import { getKernelStatus } from '../api/obsidiaClient'
import type { KernelStatus } from '../types/obsidia'
import { KERNEL_STATUS } from '../data/mockData'

const INVARIANTS = [
  { label: 'decision_authority',       value: 'KX108_ONLY', cls: 'text-obs-kernel' },
  { label: 'emits_act',                value: 'false',       cls: 'text-obs-block' },
  { label: 'memory_write',             value: 'false',       cls: 'text-obs-block' },
  { label: 'auto_promotion_allowed',   value: 'false',       cls: 'text-obs-block' },
  { label: 'graphiti_write',           value: 'false',       cls: 'text-obs-block' },
  { label: 'real_chain_action_allowed',value: 'false',       cls: 'text-obs-block' },
  { label: 'gencoin_is_real_token',    value: 'false',       cls: 'text-obs-block' },
]

const STACK = [
  { step: 1, label: 'X-108 decides',          cls: 'text-obs-kernel' },
  { step: 2, label: 'OS3 proves',             cls: 'text-obs-proof' },
  { step: 3, label: 'PoG qualifies',          cls: 'text-obs-proof' },
  { step: 4, label: 'SovereignTicket auth',   cls: 'text-obs-kernel' },
  { step: 5, label: 'Gateway controls egress', cls: 'text-obs-world' },
  { step: 6, label: 'WorldActionBus traces',  cls: 'text-obs-world' },
  { step: 7, label: 'Gencoin values (post-proof)', cls: 'text-obs-gencoin' },
  { step: 8, label: 'Brody responds',         cls: 'text-obs-brody' },
  { step: 9, label: 'Memory contextualizes',  cls: 'text-obs-memory' },
]

export function X108View() {
  const [kernel, setKernel] = useState<KernelStatus>(KERNEL_STATUS)
  const [src, setSrc] = useState<'api' | 'mock'>('mock')
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const r = await getKernelStatus()
      setKernel(r.data)
      setSrc(r.source)
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Shield size={13} className="text-obs-kernel" />
        <span className="text-obs-text font-mono text-sm font-semibold">X-108 Governance Kernel</span>
        <button onClick={load} disabled={loading} className="ml-auto p-1 text-obs-dtext hover:text-obs-text transition-colors disabled:opacity-50">
          <RefreshCw size={10} className={loading ? 'animate-spin' : ''} />
        </button>
        <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded ${src === 'api' ? 'text-obs-pass bg-obs-pass/10' : 'text-obs-hold bg-obs-hold/10'}`}>
          {src.toUpperCase()}
        </span>
      </div>

      {/* Kernel status card */}
      <div className="bg-obs-surface border border-obs-kernel/30 rounded-lg p-4">
        <div className="flex items-center gap-3 mb-3">
          <span className="w-2 h-2 rounded-full bg-obs-pass animate-pulse" />
          <span className="text-obs-kernel font-mono text-base font-bold">KERNEL: {kernel.kernel_id}</span>
          <span className="obs-badge-kernel">{kernel.status}</span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
          <div className="flex justify-between gap-2"><span className="text-obs-dtext">tests_passing</span><span className="text-obs-pass font-semibold">{kernel.tests_passing}</span></div>
          <div className="flex justify-between gap-2"><span className="text-obs-dtext">readonly</span><span className="text-obs-pass">true</span></div>
          <div className="flex justify-between gap-2"><span className="text-obs-dtext">protected_files</span><span className="text-obs-pass">clean</span></div>
          <div className="flex justify-between gap-2"><span className="text-obs-dtext">last_checked</span><span className="text-obs-mtext">{new Date(kernel.last_checked).toLocaleTimeString()}</span></div>
        </div>
      </div>

      {/* 7 non-sovereignty invariants */}
      <div>
        <div className="flex items-center gap-1.5 mb-2">
          <CheckCircle size={11} className="text-obs-pass" />
          <span className="text-obs-dtext text-[10px] font-mono font-semibold uppercase tracking-wider">Non-Sovereignty Invariants (7)</span>
        </div>
        <div className="bg-obs-surface border border-obs-border rounded-lg p-3 space-y-0.5">
          {INVARIANTS.map(inv => (
            <div key={inv.label} className="flex items-center justify-between py-0.5">
              <span className="text-obs-dtext text-[10px] font-mono">{inv.label}</span>
              <span className={`text-[10px] font-mono font-semibold ${inv.cls}`}>{inv.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Governance stack */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Governance Stack</div>
        <div className="space-y-1">
          {STACK.map((s, i) => (
            <div key={s.step} className="flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-obs-muted/40 border border-obs-border flex items-center justify-center text-[9px] font-mono text-obs-dtext shrink-0">{s.step}</span>
              <span className={`text-[10px] font-mono ${s.cls}`}>{s.label}</span>
              {i < STACK.length - 1 && (
                <span className="text-obs-dtext text-[9px] font-mono ml-auto">→</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Protected boundary */}
      <div className="rounded-lg border border-obs-kernel/20 bg-obs-kernel/5 p-3 text-[9px] font-mono text-obs-mtext space-y-0.5">
        <div className="text-obs-kernel font-semibold mb-1">X-108 PROTECTED BOUNDARY</div>
        <div>sigma/guard.py · sigma/contracts.py · sigma/protocols.py</div>
        <div>proofs/lean/ · formal/tla/ · merkle_seal.json</div>
        <div className="mt-1 text-obs-dtext">No periphery can modify these files. Brody cannot bypass this boundary.</div>
      </div>
    </div>
  )
}
