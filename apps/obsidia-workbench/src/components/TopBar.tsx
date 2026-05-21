// OBSIDIA-UI-IMPROVEMENT: TopBar — V18 badge, mode chip, git branch, tooltips
import { Shield, CheckCircle, Lock, AlertTriangle, GitBranch } from 'lucide-react'
import type { KernelStatus } from '../types/obsidia'
import type { DetectedLanguage } from '../lib/language'

interface Props {
  kernel: KernelStatus
  sessionLanguage?: DetectedLanguage
  v18HashStatus?: 'PASS' | 'FAIL' | 'UNKNOWN'
  gitBranch?: string
  mode?: 'READ_ONLY' | 'PROPOSE' | 'APPLY'
  onModeChange?: (m: 'READ_ONLY' | 'PROPOSE' | 'APPLY') => void
}

const MODE_COLORS: Record<string, string> = {
  READ_ONLY: 'bg-obs-pass/10 text-obs-pass border-obs-pass/30',
  PROPOSE:  'bg-obs-hold/10 text-obs-hold border-obs-hold/30',
  APPLY:    'bg-obs-block/10 text-obs-block border-obs-block/30',
}

export function TopBar({
  kernel, sessionLanguage = 'fr', v18HashStatus = 'UNKNOWN',
  gitBranch = 'ci-strict-sigma', mode = 'READ_ONLY', onModeChange,
}: Props) {
  const nextMode = (m: string) => {
    if (m === 'READ_ONLY') return 'PROPOSE'
    if (m === 'PROPOSE') return 'APPLY'
    return 'READ_ONLY'
  }

  return (
    <header className="h-11 bg-obs-surface border-b border-obs-border flex items-center px-4 gap-3 shrink-0 z-50">
      {/* Left: logo + kernel + ACTIVE */}
      <div className="flex items-center gap-2" title="Obsidia X-108 Workbench — Governance Kernel">
        <Shield size={14} className="text-obs-kernel" />
        <span className="text-obs-text font-mono text-xs font-semibold tracking-wider">
          OBSIDIA X-108
        </span>
        <span className="text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded bg-obs-memory/10 text-obs-memory border border-obs-memory/20">
          v2
        </span>
      </div>

      <div className="h-4 w-px bg-obs-border" />

      <div className="flex items-center gap-1.5" title={`Kernel: ${kernel.kernel_id} — Status: ${kernel.status}`}>
        <span className={`w-1.5 h-1.5 rounded-full ${kernel.status === 'ACTIVE' ? 'bg-obs-pass animate-pulse' : kernel.status === 'DEGRADED' ? 'bg-obs-hold' : 'bg-obs-block'}`} />
        <span className="text-obs-kernel font-mono text-xs font-semibold">
          KERNEL: {kernel.kernel_id}
        </span>
        <span className={`text-[9px] font-mono px-1 rounded ${kernel.status === 'ACTIVE' ? 'obs-badge-kernel' : 'obs-badge-block'}`}>
          {kernel.status}
        </span>
      </div>

      <div className="h-4 w-px bg-obs-border" />

      {/* Center: branch + tests */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1" title={`Git branch: ${gitBranch}`}>
          <GitBranch size={10} className="text-obs-dtext" />
          <span className="text-obs-dtext font-mono text-[9px]">{gitBranch}</span>
        </div>

        <div className="flex items-center gap-1" title={`${kernel.tests_passing} tests passing`}>
          <CheckCircle size={11} className="text-obs-pass" />
          <span className="text-obs-pass font-mono text-[10px] font-semibold">
            {kernel.tests_passing} TESTS
          </span>
        </div>
      </div>

      <div className="h-4 w-px bg-obs-border" />

      {/* Right: V18 badge + mode + language */}
      <div className="ml-auto flex items-center gap-2">
        {/* V18 Hash Badge */}
        <div
          className={`flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-mono font-semibold border ${
            v18HashStatus === 'PASS'
              ? 'bg-obs-pass/10 text-obs-pass border-obs-pass/20'
              : v18HashStatus === 'FAIL'
              ? 'bg-obs-block/10 text-obs-block border-obs-block/20 animate-pulse'
              : 'bg-obs-muted/20 text-obs-dtext border-obs-border/40'
          }`}
          title={v18HashStatus === 'FAIL' ? '⚠ V18 hash mismatch — kernel integrity may be compromised' : v18HashStatus === 'PASS' ? 'V18 hash verified' : 'V18 hash status unknown'}
        >
          {v18HashStatus === 'FAIL' && <AlertTriangle size={9} className="text-obs-block" />}
          V18 {v18HashStatus}
        </div>

        {/* Mode chip */}
        <button
          onClick={() => onModeChange?.(nextMode(mode) as 'READ_ONLY' | 'PROPOSE' | 'APPLY')}
          className={`flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-mono font-semibold border transition-colors ${MODE_COLORS[mode]}`}
          title={`Current mode: ${mode}. Click to cycle: READ_ONLY → PROPOSE → APPLY`}
        >
          <Lock size={9} />
          {mode}
        </button>

        {/* Language */}
        <div className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-obs-memory/10 border border-obs-memory/20" title="Session language">
          <span className="text-obs-dtext font-mono text-[9px]">LANG:</span>
          <span className="text-obs-memory font-mono text-[9px] font-semibold">{sessionLanguage.toUpperCase()}</span>
        </div>

        {/* Decision authority + timestamp */}
        <div className="hidden lg:flex items-center gap-2">
          <span className="text-obs-dtext font-mono text-[10px]" title="Sole decision authority">
            decision_authority: <span className="text-obs-kernel">KX108_ONLY</span>
          </span>
          <span className="text-obs-dtext font-mono text-[10px]" title="Last kernel check">
            {new Date(kernel.last_checked).toLocaleTimeString()}
          </span>
        </div>
      </div>
    </header>
  )
}
