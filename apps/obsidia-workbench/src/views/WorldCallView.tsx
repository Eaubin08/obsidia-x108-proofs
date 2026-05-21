import { Globe } from 'lucide-react'
import { MOCK_WORLD_CALLS, MOCK_SOVEREIGN_TICKET } from '../data/mockData'

function classColor(c: string) {
  if (c.includes('FORBIDDEN')) return 'text-obs-block'
  if (c.includes('READ')) return 'text-obs-pass'
  return 'text-obs-hold'
}

function gateClass(r: string) {
  return r === 'ALLOW' ? 'obs-badge-pass' : r === 'BLOCK' ? 'obs-badge-block' : 'obs-badge-hold'
}

export function WorldCallView() {
  const svt = MOCK_SOVEREIGN_TICKET
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Globe size={13} className="text-obs-world" />
        <span className="text-obs-text font-mono text-sm font-semibold">WorldCall / Gateway</span>
        <span className="ml-auto text-[9px] font-mono px-1.5 py-0.5 rounded text-obs-hold bg-obs-hold/10">MOCK</span>
      </div>

      <div className="rounded-lg border border-obs-block/20 bg-obs-block/5 p-3 text-[9px] font-mono text-obs-mtext">
        <div className="text-obs-block font-semibold mb-1">DRY-RUN ONLY — NO REAL EGRESS</div>
        <div>dry_run_only=true · real_action_blocked=true · egress_allowed=false</div>
        <div className="mt-0.5 text-obs-dtext">WorldCall ne peut initier aucune action réelle sans SovereignTicket X-108 valide.</div>
      </div>

      {/* Sovereign ticket */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Sovereign Ticket</div>
        <div className="bg-obs-surface border border-obs-kernel/20 rounded-lg p-3 text-[10px] font-mono space-y-0.5">
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">ticket_id</span><span className="text-obs-kernel">{svt.ticket_id}</span></div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">issued_for</span><span className="text-obs-mtext">{svt.issued_for}</span></div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">authorized_by</span><span className="text-obs-kernel">{svt.authorized_by}</span></div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">world_call_class</span><span className="text-obs-pass">{svt.world_call_class}</span></div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">dry_run_only</span><span className="text-obs-pass">true</span></div>
          <div className="flex justify-between gap-4"><span className="text-obs-dtext">real_action_blocked</span><span className="text-obs-block">{String(!svt.dry_run_only)}</span></div>
        </div>
      </div>

      {/* World calls */}
      <div>
        <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">WorldCall Events</div>
        <div className="space-y-2">
          {MOCK_WORLD_CALLS.map(wc => (
            <div key={wc.event_id} className="bg-obs-surface border border-obs-border rounded-lg p-3">
              <div className="flex items-center justify-between mb-1.5">
                <span className={`text-[10px] font-mono font-semibold ${classColor(wc.world_call_class)}`}>
                  {wc.world_call_class}
                </span>
                <span className={gateClass(wc.gateway_result)}>{wc.gateway_result}</span>
              </div>
              <p className="text-obs-mtext text-[10px] font-mono mb-1.5">{wc.action_description}</p>
              <div className="flex gap-3 text-[9px] font-mono text-obs-dtext">
                <span>dry_run=<span className="text-obs-pass">true</span></span>
                <span>real_action=<span className="text-obs-block">false</span></span>
                <span className="ml-auto">{new Date(wc.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
