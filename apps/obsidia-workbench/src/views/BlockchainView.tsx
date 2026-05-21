import { Link } from 'lucide-react'

const BLOCKS = [
  { label: 'wallet_signing',       status: 'BLOCKED', cls: 'text-obs-block' },
  { label: 'chain_transaction',    status: 'BLOCKED', cls: 'text-obs-block' },
  { label: 'smart_contract_deploy',status: 'BLOCKED', cls: 'text-obs-block' },
  { label: 'token_mint',           status: 'BLOCKED', cls: 'text-obs-block' },
  { label: 'token_transfer',       status: 'BLOCKED', cls: 'text-obs-block' },
  { label: 'gencoin_is_real_token',status: 'false',   cls: 'text-obs-block' },
  { label: 'real_chain_action',    status: 'BLOCKED', cls: 'text-obs-block' },
  { label: 'egress_to_chain',      status: 'DRY_RUN_ONLY', cls: 'text-obs-hold' },
]

export function BlockchainView() {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Link size={13} className="text-obs-mtext" />
        <span className="text-obs-text font-mono text-sm font-semibold">Blockchain Gate</span>
        <span className="ml-auto text-[9px] font-mono px-1.5 py-0.5 rounded text-obs-hold bg-obs-hold/10">MOCK</span>
      </div>

      <div className="rounded-lg border border-obs-block/30 bg-obs-block/5 p-4 space-y-1.5">
        <div className="text-obs-block font-mono text-xs font-bold">NO REAL CHAIN INTERACTION</div>
        <div className="text-[10px] font-mono text-obs-mtext space-y-0.5">
          <div>Brody ne peut pas signer de transaction blockchain.</div>
          <div>Brody ne peut pas déployer de contrat intelligent.</div>
          <div>Brody ne peut pas initier de transfert de token.</div>
          <div>Gencoin n'est pas un vrai token. Aucun contrat. Aucun wallet.</div>
        </div>
      </div>

      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Boundary Status</div>
        <div className="bg-obs-surface border border-obs-border rounded-lg p-3 space-y-1 text-[10px] font-mono">
          {BLOCKS.map(b => (
            <div key={b.label} className="flex items-center justify-between">
              <span className="text-obs-dtext">{b.label}</span>
              <span className={`font-semibold ${b.cls}`}>{b.status}</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Gateway Behavior</div>
        <div className="space-y-1.5 text-[10px] font-mono">
          <div className="px-3 py-2 rounded-lg bg-obs-surface border border-obs-border">
            <span className="text-obs-dtext">READ_ONLY_WORLD_CALL</span>
            <span className="ml-2 text-obs-pass">ALLOW (dry-run)</span>
          </div>
          <div className="px-3 py-2 rounded-lg bg-obs-surface border border-obs-border">
            <span className="text-obs-dtext">IRREVERSIBLE_WORLD_CALL</span>
            <span className="ml-2 text-obs-block">BLOCKED</span>
          </div>
          <div className="px-3 py-2 rounded-lg bg-obs-surface border border-obs-border">
            <span className="text-obs-dtext">FORBIDDEN_WORLD_CALL</span>
            <span className="ml-2 text-obs-block">BLOCKED</span>
          </div>
          <div className="px-3 py-2 rounded-lg bg-obs-surface border border-obs-border">
            <span className="text-obs-dtext">Any chain action</span>
            <span className="ml-2 text-obs-block">BLOCKED — no SovereignTicket</span>
          </div>
        </div>
      </div>

      <div className="text-[9px] font-mono text-obs-dtext p-3 rounded-lg border border-obs-border">
        real_chain_action_allowed=<span className="text-obs-block">false</span> ·
        WorldActionBus traces all egress attempts ·
        SovereignTicket required for any non-dry-run action
      </div>
    </div>
  )
}
