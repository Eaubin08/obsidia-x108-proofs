import { Coins } from 'lucide-react'
import { MOCK_GENCOIN } from '../data/mockData'

export function GencoinView() {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Coins size={13} className="text-obs-gencoin" />
        <span className="text-obs-text font-mono text-sm font-semibold">Gencoin Ledger</span>
        <span className="ml-auto text-[9px] font-mono px-1.5 py-0.5 rounded text-obs-hold bg-obs-hold/10">MOCK</span>
      </div>

      {/* Not-a-token banner */}
      <div className="rounded-lg border border-obs-gencoin/30 bg-obs-gencoin/5 p-4 space-y-1">
        <div className="text-obs-gencoin font-mono text-xs font-bold">⚠ GENCOIN IS NOT A REAL TOKEN</div>
        <div className="text-[10px] font-mono text-obs-mtext space-y-0.5">
          <div>is_real_token = <span className="text-obs-block">false</span></div>
          <div>post_proof_only = <span className="text-obs-pass">true</span></div>
          <div>ledger_only = <span className="text-obs-pass">true</span></div>
          <div>no_smart_contract · no_wallet · no_deployment · no_trade · no_mint</div>
          <div className="mt-1 text-obs-dtext">Valeur symbolique uniquement, attribuée après validation OS3. Aucune connexion blockchain réelle.</div>
        </div>
      </div>

      {/* Ledger entries */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Ledger Entries (append-only)</div>
        <div className="space-y-3">
          {MOCK_GENCOIN.map(gc => (
            <div key={gc.entry_id} className="bg-obs-surface border border-obs-border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-obs-gencoin font-mono text-lg font-bold">{gc.amount_symbolic} GC</span>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-obs-gencoin/10 text-obs-gencoin border border-obs-gencoin/20">LEDGER ONLY</span>
              </div>
              <p className="text-obs-mtext text-[10px] font-mono mb-3">{gc.description}</p>
              <div className="space-y-0.5 text-[10px] font-mono">
                <div className="flex justify-between"><span className="text-obs-dtext">proof_ref</span><span className="text-obs-proof">{gc.proof_ref}</span></div>
                <div className="flex justify-between"><span className="text-obs-dtext">is_real_token</span><span className="text-obs-block">false</span></div>
                <div className="flex justify-between"><span className="text-obs-dtext">post_proof_only</span><span className="text-obs-pass">true</span></div>
                <div className="flex justify-between"><span className="text-obs-dtext">ledger_only</span><span className="text-obs-pass">true</span></div>
                <div className="flex justify-between"><span className="text-obs-dtext">timestamp</span><span className="text-obs-mtext">{new Date(gc.timestamp).toLocaleString()}</span></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="text-[9px] font-mono text-obs-dtext p-3 rounded-lg border border-obs-border space-y-0.5">
        <div>Gencoin valorise après preuve OS3. Aucun wallet. Aucun trade. Aucun déploiement.</div>
        <div>Brody ne peut pas lire ni écrire dans ce ledger depuis une action décisionnelle.</div>
        <div>decision_authority = <span className="text-obs-kernel">KX108_ONLY</span></div>
      </div>
    </div>
  )
}
