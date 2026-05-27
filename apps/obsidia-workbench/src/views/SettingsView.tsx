import { Settings } from 'lucide-react'
import { config } from '../api/obsidiaClient'
import type { DetectedLanguage } from '../lib/language'

interface Props {
  sessionLanguage: DetectedLanguage
}

export function SettingsView({ sessionLanguage }: Props) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Settings size={13} className="text-obs-mtext" />
        <span className="text-obs-text font-mono text-sm font-semibold">Settings</span>
      </div>

      {/* API config */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">API Configuration</div>
        <div className="bg-obs-surface border border-obs-border rounded-lg p-3 space-y-0.5 text-[10px] font-mono">
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">VITE_OBSIDIA_API_BASE</span><span className="text-obs-mtext">{config.API_BASE}</span></div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">VITE_ENGINE_API_BASE</span><span className="text-obs-mtext">{config.ENGINE_BASE}</span></div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">VITE_USE_MOCK_FALLBACK</span>
            <span className={config.USE_MOCK ? 'text-obs-hold' : 'text-obs-pass'}>{String(config.USE_MOCK)}</span>
          </div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">VITE_PROBE_TIMEOUT_MS</span><span className="text-obs-mtext">{config.TIMEOUT_MS}</span></div>
        </div>
      </div>

      {/* Language */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Language</div>
        <div className="bg-obs-surface border border-obs-border rounded-lg p-3 text-[10px] font-mono space-y-0.5">
          <div className="flex justify-between"><span className="text-obs-dtext">session_language</span><span className="text-obs-memory">{sessionLanguage.toUpperCase()}</span></div>
          <div className="flex justify-between"><span className="text-obs-dtext">default_language</span><span className="text-obs-mtext">fr</span></div>
          <div className="flex justify-between"><span className="text-obs-dtext">auto_detect</span><span className="text-obs-pass">true</span></div>
          <div className="flex justify-between"><span className="text-obs-dtext">supported</span><span className="text-obs-mtext">fr · en · mixed</span></div>
        </div>
      </div>

      {/* How to change config */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Override Config</div>
        <div className="bg-obs-surface border border-obs-border rounded-lg p-3 text-[9px] font-mono text-obs-mtext space-y-1">
          <div className="text-obs-dtext mb-1">Create <span className="text-obs-memory">.env.local</span> in apps/obsidia-workbench/:</div>
          <div className="text-obs-mtext">VITE_OBSIDIA_API_BASE=http://127.0.0.1:8011</div>
          <div className="text-obs-mtext">VITE_ENGINE_API_BASE=http://127.0.0.1:8012</div>
          <div className="text-obs-mtext">VITE_USE_MOCK_FALLBACK=true</div>
          <div className="text-obs-mtext">VITE_PROBE_TIMEOUT_MS=3000</div>
          <div className="mt-2 text-obs-dtext">Restart dev server after changes.</div>
        </div>
      </div>

      {/* Sovereignty invariants reminder */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Sovereignty Constraints (immutable)</div>
        <div className="bg-obs-kernel/5 border border-obs-kernel/20 rounded-lg p-3 text-[9px] font-mono text-obs-mtext space-y-0.5">
          <div>No real action · No memory write · No wallet · No payment</div>
          <div>No trade · No API mutation · No kernel mutation · No ACT emit</div>
          <div className="mt-1 text-obs-dtext">Ces contraintes sont invariantes et non configurables.</div>
        </div>
      </div>
    </div>
  )
}
