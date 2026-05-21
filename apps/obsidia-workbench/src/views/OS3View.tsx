import { FileCode } from 'lucide-react'
import { MOCK_OS3_TICKET } from '../data/mockData'

export function OS3View() {
  const t = MOCK_OS3_TICKET
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="flex items-center gap-2">
        <FileCode size={13} className="text-obs-proof" />
        <span className="text-obs-text font-mono text-sm font-semibold">OS3 Formal Proof System</span>
        <span className="ml-auto text-[9px] font-mono px-1.5 py-0.5 rounded text-obs-hold bg-obs-hold/10">MOCK</span>
      </div>

      <div className="rounded-lg border border-obs-proof/20 bg-obs-proof/5 p-3 text-[9px] font-mono text-obs-mtext">
        <div className="text-obs-proof font-semibold mb-1">OS3 PROOF SYSTEM</div>
        OS3 prouve chaque décision X-108 via Lean 4 et TLA+. Le hash Merkle ancre la chaîne. OS3 ne décide pas — il prouve.
      </div>

      {/* Ticket */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Active Proof Ticket</div>
        <div className="bg-obs-surface border border-obs-border rounded-lg p-4 space-y-1 text-[10px] font-mono">
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">ticket_id</span><span className="text-obs-proof">{t.ticket_id}</span></div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">action_id</span><span className="text-obs-mtext">{t.action_id}</span></div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">status</span>
            <span className={t.status === 'PROOF_VALID' ? 'text-obs-pass font-semibold' : 'text-obs-hold'}>{t.status}</span>
          </div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">os3_proves</span><span className="text-obs-pass">true</span></div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">kernel_decides</span><span className="text-obs-kernel">true</span></div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">timestamp</span><span className="text-obs-mtext">{new Date(t.timestamp).toLocaleString()}</span></div>
        </div>
      </div>

      {/* Proof refs */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Proof References</div>
        <div className="space-y-2">
          <div className="bg-obs-surface border border-obs-border rounded-lg p-3 text-[10px] font-mono">
            <div className="text-obs-dtext mb-1">lean_ref</div>
            <div className="text-obs-proof">{t.lean_ref}</div>
          </div>
          <div className="bg-obs-surface border border-obs-border rounded-lg p-3 text-[10px] font-mono">
            <div className="text-obs-dtext mb-1">tla_ref</div>
            <div className="text-obs-proof">{t.tla_ref}</div>
          </div>
          <div className="bg-obs-surface border border-obs-border rounded-lg p-3 text-[10px] font-mono">
            <div className="text-obs-dtext mb-1">merkle_hash</div>
            <div className="text-obs-mtext break-all">{t.merkle_hash}</div>
          </div>
        </div>
      </div>

      <div className="rounded-lg border border-obs-border p-3 text-[9px] font-mono text-obs-dtext space-y-0.5">
        <div>merkle_seal.json — FROZEN — DO NOT TOUCH</div>
        <div>rfc3161 timestamp — FROZEN — DO NOT TOUCH</div>
        <div>proofs/lean/ — PROTECTED — SEALED</div>
        <div>formal/tla/ — PROTECTED — SEALED</div>
      </div>
    </div>
  )
}
