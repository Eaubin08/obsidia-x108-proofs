// OBSIDIA-UI-IMPROVEMENT: RightPanel — clickable copy, tree_X prompts, v18 hash, git branch, refresh context
import { useState } from 'react'
import {
  MOCK_CONTEXT_PACKET, MOCK_OS3_TICKET, MOCK_SOVEREIGN_TICKET,
  MOCK_WORLD_CALLS, MOCK_MEMORY_CANDIDATES, MOCK_GENCOIN, MOCK_AUDIT,
} from '../data/mockData'
import { FileText, Shield, Database, Coins, ClipboardList, Wifi, Copy, Check, RefreshCw, Cpu } from 'lucide-react'
import { BackendStatusPanel } from './BackendStatusPanel'
import type { AutomationSnapshot, StructuredResponseSnapshot, FreezeMetricsSnapshot } from '../api/contracts'

const TABS = [
  { id: 'context',    label: 'CONTEXT',    icon: FileText },
  { id: 'governance', label: 'GOV',        icon: Shield },
  { id: 'memory',     label: 'MEMORY',     icon: Database },
  { id: 'gencoin',    label: 'GENCOIN',    icon: Coins },
  { id: 'audit',      label: 'AUDIT',      icon: ClipboardList },
  { id: 'automation', label: 'AUTOMATION', icon: Cpu },
  { id: 'backend',    label: 'BACKEND',    icon: Wifi },
  { id: 'freeze',     label: 'FREEZE',     icon: Shield },
] as const
type TabId = typeof TABS[number]['id']

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <div className="obs-section-header px-0 pt-0 pb-1.5">{children}</div>
}

function CopyableKV({ k, v, vClass }: { k: string; v: string; vClass?: string }) {
  const [copied, setCopied] = useState(false)
  const handleClick = async () => {
    await navigator.clipboard.writeText(v)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }
  return (
    <div className="flex items-start gap-2 py-0.5 group cursor-pointer hover:bg-obs-muted/10 rounded px-0.5" onClick={handleClick} title="Click to copy">
      <span className="text-obs-dtext font-mono text-[10px] shrink-0 w-32">{k}</span>
      <span className={`font-mono text-[10px] break-all ${vClass ?? 'text-obs-mtext'}`}>{v}</span>
      <span className="ml-auto opacity-0 group-hover:opacity-100 shrink-0">
        {copied ? <Check size={9} className="text-obs-pass" /> : <Copy size={9} className="text-obs-dtext" />}
      </span>
    </div>
  )
}

function CopyableBool({ k, v }: { k: string; v: boolean }) {
  return <CopyableKV k={k} v={String(v)} vClass={v ? 'text-obs-pass' : 'text-obs-block'} />
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {}
}

function textList(value: unknown): string {
  if (Array.isArray(value)) return value.length ? value.map(String).join(', ') : '—'
  if (value === undefined || value === null || value === '') return '—'
  return String(value)
}

function boolLike(value: unknown): string {
  if (value === true) return 'true'
  if (value === false) return 'false'
  if (value === undefined || value === null || value === '') return '—'
  return String(value)
}


function TrueVoiceSection({ live }: { live: Record<string, unknown> }) {
  const tv = asRecord(live.true_voice_snapshot)
  const trs = asRecord(live.true_response_structure_snapshot)

  if (!Object.keys(tv).length && !Object.keys(trs).length) return null

  return (
    <div>
      <SectionTitle>True Voice / LLM Obsidien</SectionTitle>
      <div className="obs-card p-3 space-y-0.5 border-obs-brody/30 bg-obs-brody/5">
        <CopyableKV k="status" v={String(tv.status ?? '—')} vClass={String(tv.status ?? '').includes('PASS') ? 'text-obs-pass' : 'text-obs-hold'} />
        <CopyableKV k="voice_source" v={String(tv.voice_source ?? tv.final_answer_source ?? '—')} vClass="text-obs-brody" />
        <CopyableKV k="final_answer_source" v={String(tv.final_answer_source ?? '—')} vClass="text-obs-brody" />
        <CopyableKV k="source_mode" v={String(tv.source_mode ?? '—')} />
        <CopyableKV k="domain_voice_mode" v={String(tv.domain_voice_mode ?? '—')} vClass={String(tv.domain_voice_mode ?? '').includes('DOMAIN') ? 'text-obs-pass' : 'text-obs-dtext'} />
        <CopyableKV k="model_position" v={String(trs.model_position ?? 'LLM_OBSIDIEN_READONLY_ADVISORY')} vClass="text-obs-proof" />
        <CopyableKV k="structure_first" v="true" vClass="text-obs-pass" />
        <CopyableKV k="memory_enrichment" v="optional" vClass="text-obs-memory" />
        <CopyableKV k="decision_authority" v={String(live.decision_authority ?? 'KX108_ONLY')} vClass="text-obs-kernel" />
      </div>
    </div>
  )
}

function DomainRaccordSection({ live }: { live: Record<string, unknown> }) {
  const tv = asRecord(live.true_voice_snapshot)
  const support = asRecord(live.support_summary)

  const tvDomain = asRecord(tv.domain_raccord_snapshot)
  const supportDomain = asRecord(support.domain_raccord_snapshot)
  const domain = Object.keys(tvDomain).length > 0 ? tvDomain : supportDomain

  const domains = Array.isArray(tv.domain_raccord_domains)
    ? tv.domain_raccord_domains
    : Array.isArray(domain.domains)
      ? domain.domains
      : []

  if (!Object.keys(domain).length && domains.length === 0) return null

  return (
    <div>
      <SectionTitle>Domain Raccord / Structure-First</SectionTitle>
      <div className="obs-card p-3 space-y-0.5 border-obs-proof/30 bg-obs-proof/5">
        <CopyableKV k="status" v={String(domain.status ?? '—')} vClass={String(domain.status ?? '').includes('READY') ? 'text-obs-pass' : 'text-obs-hold'} />
        <CopyableKV k="voice_mode" v={String(domain.voice_mode ?? tv.domain_voice_mode ?? '—')} vClass="text-obs-brody" />
        <CopyableKV k="domains" v={textList(domains)} vClass="text-obs-proof" />
        <CopyableKV k="structural_answer_available" v={boolLike(domain.structural_answer_available)} vClass={domain.structural_answer_available === true ? 'text-obs-pass' : 'text-obs-hold'} />
        <CopyableKV k="negation_guard_active" v={boolLike(domain.negation_guard_active)} vClass={domain.negation_guard_active === true ? 'text-obs-pass' : 'text-obs-dtext'} />
        <CopyableKV k="write_boundary_required" v={boolLike(domain.write_boundary_required)} vClass={domain.write_boundary_required === true ? 'text-obs-block' : 'text-obs-dtext'} />
        <CopyableKV k="memory_dependency" v={String(domain.memory_dependency ?? 'NONE')} vClass="text-obs-pass" />
        <CopyableKV k="memory_enrichment" v={String(domain.memory_enrichment ?? 'OPTIONAL')} vClass="text-obs-memory" />
        <CopyableKV k="priority" v="domain_raccord_first; memory=enrichment_only; authority=KX108_ONLY" vClass="text-obs-kernel" />
      </div>
    </div>
  )
}

function AdaptiveSigmaSection({ live }: { live: Record<string, unknown> }) {
  const tv  = asRecord(live.true_voice_snapshot)
  const pol = asRecord(tv.adaptive_response_policy)

  if (!Object.keys(pol).length) return null

  const sizeColor = (s: unknown) =>
    s === 'BOUNDARY_COMPACT' ? 'text-obs-block' :
    s === 'DEEP'             ? 'text-obs-brody' :
    s === 'MEDIUM'           ? 'text-obs-pass'  : 'text-obs-dtext'

  const pressureColor = (p: unknown) =>
    p === 'HIGH'   ? 'text-obs-block' :
    p === 'MEDIUM' ? 'text-obs-hold'  : 'text-obs-pass'

  return (
    <div>
      <SectionTitle>Adaptive Response Policy / Sigma</SectionTitle>
      <div className="obs-card p-3 space-y-0.5 border-obs-hold/30 bg-obs-hold/5">
        <CopyableKV k="status"                v={String(pol.status ?? '—')}                vClass={String(pol.status ?? '').includes('READY') ? 'text-obs-pass' : 'text-obs-hold'} />
        <CopyableKV k="response_size"         v={String(pol.response_size ?? '—')}         vClass={sizeColor(pol.response_size)} />
        <CopyableKV k="density"               v={String(pol.density ?? '—')}               vClass="text-obs-mtext" />
        <CopyableKV k="context_need"          v={String(pol.context_need ?? '—')}          vClass="text-obs-brody" />
        <CopyableKV k="sigma_pressure"        v={String(pol.sigma_pressure ?? '—')}        vClass={pressureColor(pol.sigma_pressure)} />
        <CopyableKV k="reason"                v={String(pol.reason ?? '—')} />
        <CopyableKV k="observed_answer_size"  v={String(pol.observed_answer_size ?? '—')} />
        <CopyableKV k="observed_answer_words" v={String(pol.observed_answer_words ?? '—')} />
        <CopyableKV k="boundary_detected"     v={boolLike(pol.boundary_detected)}          vClass={pol.boundary_detected === true ? 'text-obs-block' : 'text-obs-dtext'} />
        <CopyableKV k="decision_authority"    v={String(pol.decision_authority ?? 'KX108_ONLY')} vClass="text-obs-kernel" />
        <CopyableKV k="readonly"              v={boolLike(pol.readonly)}                   vClass="text-obs-pass" />
      </div>
    </div>
  )
}

function BoundaryEnvelopeSection({ live }: { live: Record<string, unknown> }) {
  return (
    <div>
      <SectionTitle>12E6 Boundary Envelope</SectionTitle>
      <div className="obs-card p-3 space-y-0.5 border-obs-block/25 bg-obs-block/5">
        <CopyableKV k="readonly" v={boolLike(live.readonly)} vClass={live.readonly === true ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="advisory_only" v={boolLike(live.advisory_only)} vClass={live.advisory_only === true ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="context_signal_only" v={boolLike(live.context_signal_only)} vClass={live.context_signal_only === true ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="allowed_to_decide" v={boolLike(live.allowed_to_decide)} vClass={live.allowed_to_decide === false ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="allowed_to_act" v={boolLike(live.allowed_to_act)} vClass={live.allowed_to_act === false ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="emits_act" v={boolLike(live.emits_act)} vClass={live.emits_act === false ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="emits_verdict" v={boolLike(live.emits_verdict)} vClass={live.emits_verdict === false ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="memory_write" v={boolLike(live.memory_write)} vClass={live.memory_write === false ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="graphiti_write" v={boolLike(live.graphiti_write)} vClass={live.graphiti_write === false ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="neo4j_write" v={boolLike(live.neo4j_write)} vClass={live.neo4j_write === false ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="kernel_mutation" v={boolLike(live.kernel_mutation)} vClass={live.kernel_mutation === false ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="x108_mutation" v={boolLike(live.x108_mutation)} vClass={live.x108_mutation === false ? 'text-obs-pass' : 'text-obs-block'} />
        <CopyableKV k="decision_authority" v={String(live.decision_authority ?? 'KX108_ONLY')} vClass="text-obs-kernel" />
      </div>
    </div>
  )
}


function NativeMachinationSection({ live }: { live: Record<string, unknown> }) {
  const hasNative = Boolean(
    live.support_summary ||
    live.contracts ||
    live.permission_matrix ||
    live.machination_packet ||
    live.boundary_contract ||
    live.kernel_contract
  )

  if (!hasNative) return null

  const support = asRecord(live.support_summary)
  const contracts = asRecord(live.contracts)
  const permissionDirect = asRecord(live.permission_matrix)
  const permissionFromContracts = asRecord(contracts.permission_matrix)
  const permission = Object.keys(permissionDirect).length > 0 ? permissionDirect : permissionFromContracts
  const boundary = Object.keys(asRecord(live.boundary_contract)).length > 0 ? asRecord(live.boundary_contract) : asRecord(contracts.boundary_contract)
  const kernel = Object.keys(asRecord(live.kernel_contract)).length > 0 ? asRecord(live.kernel_contract) : asRecord(contracts.kernel_contract)
  const signal = Object.keys(asRecord(live.signal_contract)).length > 0 ? asRecord(live.signal_contract) : asRecord(contracts.signal_contract)
  const forbidden = Object.keys(asRecord(live.forbidden_output_contract)).length > 0 ? asRecord(live.forbidden_output_contract) : asRecord(contracts.forbidden_output_contract)
  const machination = asRecord(live.machination_packet)

  const brodyPerm = asRecord(permission.brody)
  const x108Perm = asRecord(permission.x108)
  const memoryPerm = asRecord(permission.memory)
  const automationPerm = asRecord(permission.automation)
  const graphitiPerm = asRecord(permission.graphiti)
  const treePerm = asRecord(permission.trees)

  return (
    <div className="space-y-3">
      <div>
        <SectionTitle>Native Machination</SectionTitle>
        <div className="obs-card p-3 space-y-0.5 border-obs-proof/30 bg-obs-proof/5">
          <CopyableKV k="status" v={String(machination.status ?? '—')} vClass={String(machination.status ?? '').includes('READY') ? 'text-obs-pass' : 'text-obs-hold'} />
          <CopyableKV k="source" v={String(machination.source ?? '—')} vClass="text-obs-proof" />
          <CopyableKV k="support_intent" v={String(support.intent ?? '—')} vClass="text-obs-brody" />
          <CopyableKV k="risk_flags" v={textList(support.risk_flags)} vClass="text-obs-hold" />
          <CopyableKV k="contradictions" v={textList(support.contradictions)} vClass={Array.isArray(support.contradictions) && support.contradictions.length > 0 ? 'text-obs-block' : 'text-obs-dtext'} />
          <CopyableKV k="projection_mode" v={String(support.projection_mode ?? '—')} />
          <CopyableKV k="boundary_notice" v={String(support.boundary_notice ?? 'KX108_ONLY')} vClass="text-obs-kernel" />
        </div>
      </div>

      <div>
        <SectionTitle>Contracts / Permission Matrix</SectionTitle>
        <div className="obs-card p-3 space-y-0.5 border-obs-kernel/30 bg-obs-kernel/5">
          <CopyableKV k="decision_authority" v={String(live.decision_authority ?? 'KX108_ONLY')} vClass="text-obs-kernel" />
          <CopyableKV k="kernel" v={String(kernel.kernel ?? 'X108/KX108')} vClass="text-obs-kernel" />
          <CopyableKV k="brody.can_decide" v={boolLike(brodyPerm.can_decide)} vClass={brodyPerm.can_decide === false ? 'text-obs-pass' : 'text-obs-block'} />
          <CopyableKV k="brody.can_act" v={boolLike(brodyPerm.can_act)} vClass={brodyPerm.can_act === false ? 'text-obs-pass' : 'text-obs-block'} />
          <CopyableKV k="brody.can_write_memory" v={boolLike(brodyPerm.can_write_memory)} vClass={brodyPerm.can_write_memory === false ? 'text-obs-pass' : 'text-obs-block'} />
          <CopyableKV k="memory.can_commit" v={boolLike(memoryPerm.can_commit)} vClass={memoryPerm.can_commit === false ? 'text-obs-pass' : 'text-obs-block'} />
          <CopyableKV k="automation.can_execute" v={boolLike(automationPerm.can_execute)} vClass={automationPerm.can_execute === false ? 'text-obs-pass' : 'text-obs-block'} />
          <CopyableKV k="graphiti.can_write" v={boolLike(graphitiPerm.can_write)} vClass={graphitiPerm.can_write === false ? 'text-obs-pass' : 'text-obs-block'} />
          <CopyableKV k="trees.can_decide" v={boolLike(treePerm.can_decide)} vClass={treePerm.can_decide === false ? 'text-obs-pass' : 'text-obs-block'} />
          <CopyableKV k="x108.sole_decision" v={boolLike(x108Perm.sole_decision_authority)} vClass={x108Perm.sole_decision_authority === true ? 'text-obs-pass' : 'text-obs-hold'} />
        </div>
      </div>

      <div>
        <SectionTitle>Native Boundary</SectionTitle>
        <div className="obs-card p-3 space-y-0.5 border-obs-block/25 bg-obs-block/5">
          <CopyableKV k="readonly" v={boolLike(boundary.readonly ?? live.readonly)} vClass="text-obs-pass" />
          <CopyableKV k="allowed_to_decide" v={boolLike(boundary.allowed_to_decide)} vClass={boundary.allowed_to_decide === false ? 'text-obs-pass' : 'text-obs-block'} />
          <CopyableKV k="allowed_to_act" v={boolLike(boundary.allowed_to_act)} vClass={boundary.allowed_to_act === false ? 'text-obs-pass' : 'text-obs-block'} />
          <CopyableKV k="emits_act" v={boolLike(boundary.emits_act ?? live.emits_act)} vClass="text-obs-block" />
          <CopyableKV k="emits_verdict" v={boolLike(boundary.emits_verdict)} vClass="text-obs-block" />
          <CopyableKV k="memory_write" v={boolLike(boundary.memory_write ?? live.memory_write)} vClass="text-obs-block" />
          <CopyableKV k="graphiti_write" v={boolLike(boundary.graphiti_write ?? live.graphiti_write)} vClass="text-obs-block" />
          <CopyableKV k="kernel_mutation" v={boolLike(boundary.kernel_mutation ?? live.kernel_mutation)} vClass="text-obs-block" />
          <CopyableKV k="x108_mutation" v={boolLike(boundary.x108_mutation)} vClass="text-obs-block" />
          <CopyableKV k="signal_authority" v={String(signal.decision_authority ?? 'KX108_ONLY')} vClass="text-obs-kernel" />
          <CopyableKV k="forbidden_tokens" v={textList(forbidden.forbidden_tokens_as_authority)} vClass="text-obs-hold" />
        </div>
      </div>
    </div>
  )
}

function AuthoritySnapshotSection({ snap }: { snap: Record<string, unknown> }) {
  const mode = snap.response_mode as string | undefined
  const reqType = snap.request_type as string | undefined
  const may = snap.brody_may as string[] | undefined
  const mustNot = snap.brody_must_not as string[] | undefined
  const tp = snap.tree_policy as Record<string, unknown> | undefined
  const modeColor = !mode ? 'text-obs-mtext' :
    mode === 'ACTION_BOUNDARY' ? 'text-obs-block' :
    mode === 'FULL_ANSWER' ? 'text-obs-pass' :
    mode === 'ADVISORY_PRIORITY' ? 'text-obs-brody' :
    mode === 'CONTEXT_DIAGNOSTIC' ? 'text-obs-memory' :
    mode === 'MEMORY_CANDIDATE' ? 'text-obs-hold' : 'text-obs-mtext'
  return (
    <div>
      <SectionTitle>Authority Snapshot</SectionTitle>
      <div className="obs-card p-3 space-y-1 border-obs-kernel/20 bg-obs-kernel/5">
        {reqType ? <CopyableKV k="request_type" v={reqType} vClass="text-obs-brody" /> : null}
        {mode ? <CopyableKV k="response_mode" v={mode} vClass={modeColor} /> : null}
        <CopyableKV k="decision_authority" v="KX108_ONLY" vClass="text-obs-kernel" />
        {snap.requires_human_operator !== undefined ? (
          <CopyableKV k="requires_human_operator" v={String(snap.requires_human_operator)} vClass={snap.requires_human_operator ? 'text-obs-hold' : 'text-obs-dtext'} />
        ) : null}
        {snap.requires_kx108_decision !== undefined ? (
          <CopyableKV k="requires_kx108_decision" v={String(snap.requires_kx108_decision)} vClass={snap.requires_kx108_decision ? 'text-obs-block' : 'text-obs-dtext'} />
        ) : null}
        {snap.requires_memory_gate !== undefined ? (
          <CopyableKV k="requires_memory_gate" v={String(snap.requires_memory_gate)} vClass={snap.requires_memory_gate ? 'text-obs-hold' : 'text-obs-dtext'} />
        ) : null}
        {snap.requires_api_bridge_gate !== undefined ? (
          <CopyableKV k="requires_api_bridge_gate" v={String(snap.requires_api_bridge_gate)} vClass={snap.requires_api_bridge_gate ? 'text-obs-hold' : 'text-obs-dtext'} />
        ) : null}
        {may && may.length > 0 && (
          <div className="pt-1">
            <div className="text-obs-dtext text-[9px] font-mono mb-0.5">brody_may</div>
            <div className="flex flex-wrap gap-1">
              {may.slice(0, 5).map(m => (
                <span key={m} className="obs-badge-pass text-[8px]">{m.replace(/_/g, ' ')}</span>
              ))}
              {may.length > 5 ? <span className="text-obs-dtext text-[8px] font-mono">+{may.length - 5}</span> : null}
            </div>
          </div>
        )}
        {mustNot && mustNot.length > 0 && (
          <div className="pt-0.5">
            <div className="text-obs-dtext text-[9px] font-mono mb-0.5">brody_must_not</div>
            <div className="flex flex-wrap gap-1">
              {mustNot.slice(0, 4).map(m => (
                <span key={m} className="obs-badge-block text-[8px]">{m.replace(/_/g, ' ')}</span>
              ))}
              {mustNot.length > 4 ? <span className="text-obs-dtext text-[8px] font-mono">+{mustNot.length - 4}</span> : null}
            </div>
          </div>
        )}
        {tp && (
          <div className="pt-1">
            <div className="text-obs-dtext text-[9px] font-mono mb-0.5">tree_policy</div>
            <div className="flex gap-3 flex-wrap">
              <span className="text-obs-pass text-[9px] font-mono">safe: {(tp.safe_trees as string[])?.length ?? 0}</span>
              <span className="text-obs-block text-[9px] font-mono">blocked: {(tp.blocked_total as number) ?? 9}</span>
              <span className="text-obs-dtext text-[9px] font-mono">signal: {tp.signal_method as string}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function ContextTab({ onSendPrompt, live }: { onSendPrompt?: (text: string) => void; live?: Record<string, unknown> }) {
  const cp = MOCK_CONTEXT_PACKET
  const v18: string = 'FAIL'
  const liveCtx = live?.context_packet as Record<string, unknown> | undefined
  const authoritySnap = live?.authority_snapshot as Record<string, unknown> | undefined
  const memChain = live?.memory_response_chain_snapshot as Record<string, unknown> | undefined
  const semQuery = live?.semantic_query_snapshot as Record<string, unknown> | undefined
  const projMem = live?.project_memory_snapshot as Record<string, unknown> | undefined
  const candMem = live?.candidate_memory_snapshot as Record<string, unknown> | undefined
  const opLoop = live?.operator_loop_snapshot as Record<string, unknown> | undefined
  const treePol = live?.tree_policy_snapshot as Record<string, unknown> | undefined
  const temporal = live?.temporal_context_snapshot as Record<string, unknown> | undefined
  const cogMod = live?.cognitive_modules_snapshot as Record<string, unknown> | undefined
  const rtCtx = live?.runtime_context as Record<string, unknown> | undefined
  const operatorView = live?.operator_view_packet as Record<string, unknown> | undefined
  const opReadiness = operatorView?.["readiness"] as Record<string, unknown> | undefined
  const opUsable = operatorView?.["usable"] as Record<string, unknown> | undefined
  const opBlocked = operatorView?.["blocked"] as Record<string, unknown> | undefined
  const opEvidence = operatorView?.["evidence"] as Record<string, unknown> | undefined
  const opSummary = operatorView?.["summary"] as Record<string, unknown> | undefined
  return (
    <div className="space-y-4">
      {authoritySnap && Object.keys(authoritySnap).length > 0 && (
        <AuthoritySnapshotSection snap={authoritySnap} />
      )}
      {live && <TrueVoiceSection live={live} />}
      {live && <AdaptiveSigmaSection live={live} />}
      {live && <DomainRaccordSection live={live} />}
      {live && <BoundaryEnvelopeSection live={live} />}
      {live && <NativeMachinationSection live={live} />}
      {live && (
        <div>
          <SectionTitle>Live Backend — Last Response</SectionTitle>
          <div className="obs-card p-3 space-y-0.5 border-obs-brody/20 bg-obs-brody/5">
            {live.voice_runtime ? <CopyableKV k="voice_runtime" v={String(live.voice_runtime)} vClass="text-obs-brody" /> : null}
            {live.source ? <CopyableKV k="source" v={String(live.source)} vClass={
              String(live.source).includes('GRAPHITI') ? 'text-obs-pass' :
              String(live.source).includes('STUB') ? 'text-obs-hold' : 'text-obs-brody'
            } /> : null}
            {live.graphiti_status ? <CopyableKV k="graphiti_status" v={String(live.graphiti_status)} vClass={String(live.graphiti_status).includes('LIVE') ? 'text-obs-pass' : 'text-obs-hold'} /> : null}
            {live.neo4j_status ? <CopyableKV k="neo4j_status" v={String(live.neo4j_status)} vClass={live.neo4j_status === 'ONLINE' ? 'text-obs-pass' : 'text-obs-hold'} /> : null}
            <CopyableKV k="decision_authority" v={String(live.decision_authority ?? "KX108_ONLY")} vClass="text-obs-kernel" />
            <CopyableKV k="readonly" v="true" vClass="text-obs-pass" />
            <CopyableKV k="emits_act" v="false" vClass="text-obs-block" />
          </div>
        </div>
      )}
      {operatorView && (
        <div>
          <SectionTitle>Transverse Operator View</SectionTitle>
          <div className="obs-card p-3 space-y-0.5 border-obs-proof/20 bg-obs-proof/5">
            <CopyableKV k="system_status" v={String(operatorView["system_status"] ?? "-")} vClass={String(operatorView["system_status"] ?? "").includes("READY") ? "text-obs-pass" : String(operatorView["system_status"] ?? "").includes("ATTENTION") ? "text-obs-hold" : "text-obs-brody"} />
            <CopyableKV k="next_safe_action" v={String(operatorView["next_safe_action"] ?? "-")} vClass="text-obs-proof" />
            <CopyableKV k="decision_authority" v={String(operatorView["decision_authority"] ?? "KX108_ONLY")} vClass="text-obs-kernel" />
            <CopyableKV k="readonly" v={String(operatorView["readonly"] ?? true)} vClass="text-obs-pass" />
            <CopyableKV k="emits_act" v={String(operatorView["emits_act"] ?? false)} vClass="text-obs-block" />
            <CopyableKV k="emits_verdict" v={String(operatorView["emits_verdict"] ?? false)} vClass="text-obs-block" />
            {opSummary && <CopyableKV k="all_core_packets_ready" v={String(opSummary["all_core_packets_ready"] ?? false)} vClass={opSummary["all_core_packets_ready"] ? "text-obs-pass" : "text-obs-hold"} />}
            {opSummary && <CopyableKV k="safe_boundary_ok" v={String(opSummary["safe_boundary_ok"] ?? false)} vClass={opSummary["safe_boundary_ok"] ? "text-obs-pass" : "text-obs-block"} />}
            {opSummary && <CopyableKV k="operator_can_write" v={String(opSummary["operator_can_write"] ?? false)} vClass="text-obs-block" />}
            {opSummary && <CopyableKV k="operator_can_decide" v={String(opSummary["operator_can_decide"] ?? false)} vClass="text-obs-block" />}
            {opReadiness && <CopyableKV k="readiness" v={JSON.stringify(opReadiness)} />}
            {opUsable && <CopyableKV k="usable" v={JSON.stringify(opUsable)} />}
            {opBlocked && Array.isArray(opBlocked["hard_risks"]) ? (
              <CopyableKV k="hard_risks" v={JSON.stringify((opBlocked["hard_risks"] as unknown[]).slice(0, 8))} vClass={(opBlocked["hard_risks"] as unknown[]).length > 0 ? "text-obs-hold" : "text-obs-pass"} />
            ) : null}
            {opBlocked && Array.isArray(opBlocked["missing_packets"]) ? (
              <CopyableKV k="missing_packets" v={JSON.stringify((opBlocked["missing_packets"] as unknown[]).slice(0, 8))} vClass={(opBlocked["missing_packets"] as unknown[]).length > 0 ? "text-obs-hold" : "text-obs-pass"} />
            ) : null}
            {opEvidence && <CopyableKV k="memory_guard_status" v={String(opEvidence["memory_guard_status"] ?? "-")} />}
            {opEvidence && <CopyableKV k="value_layer_scores_null" v={String(opEvidence["value_layer_scores_null"] ?? "-")} vClass={opEvidence["value_layer_scores_null"] ? "text-obs-pass" : "text-obs-block"} />}
          </div>
        </div>
      )}
      {semQuery && (
        <div>
          <SectionTitle>Semantic Query Router</SectionTitle>
          <div className="obs-card p-2.5 space-y-0.5 border-obs-memory/20 bg-obs-memory/5">
            <CopyableKV k="topic" v={String(semQuery.topic ?? '—')} vClass="text-obs-memory" />
            <CopyableKV k="primary_query" v={String(semQuery.primary_query ?? '—')} />
            <CopyableKV k="semantic_query" v={String(semQuery.semantic_query ?? '—')} />
            <CopyableKV k="is_canonical" v={String(semQuery.is_canonical ?? '—')} vClass={semQuery.is_canonical ? 'text-obs-pass' : 'text-obs-hold'} />
          </div>
        </div>
      )}
      {memChain && (
        <div>
          <SectionTitle>Memory Response Chain</SectionTitle>
          <div className="obs-card p-2.5 space-y-0.5 border-obs-brody/20 bg-obs-brody/5">
            <CopyableKV k="status" v={String(memChain.status ?? '—')} vClass={String(memChain.status ?? '').includes('PASS') ? 'text-obs-pass' : 'text-obs-hold'} />
            <CopyableKV k="source_mode" v={String(memChain.source_mode ?? '—')} />
            <CopyableKV k="effective_query" v={String(memChain.effective_query ?? '—')} vClass="text-obs-brody" />
            <CopyableKV k="material_quality" v={String(memChain.material_quality ?? '—')} />
            <CopyableKV k="results_count" v={String(memChain.query_results_count ?? 0)} />
            <CopyableKV k="neo4j_status" v={String(memChain.neo4j_status ?? memChain.error ?? '—')} vClass={String(memChain.neo4j_status ?? '').includes('REACHABLE') ? 'text-obs-pass' : 'text-obs-hold'} />
            {Array.isArray(memChain.attempted_queries) && memChain.attempted_queries.length > 0 && (
              <CopyableKV k="attempted_queries" v={JSON.stringify((memChain.attempted_queries as unknown[]).slice(0, 4))} />
            )}
          </div>
        </div>
      )}
      {rtCtx && (
        <div>
          <SectionTitle>Runtime Context</SectionTitle>
          <div className="obs-card p-2.5 space-y-0.5 border-obs-kernel/30 bg-obs-kernel/5">
            <CopyableKV k="status" v={String(rtCtx.status ?? '—')} vClass={String(rtCtx.status ?? '').includes('READY') ? 'text-obs-pass' : 'text-obs-hold'} />
            <CopyableKV k="voice_source" v={String(rtCtx.voice_source ?? '—')} vClass="text-obs-brody" />
            <CopyableKV k="topic" v={String(rtCtx.topic ?? '—')} vClass="text-obs-memory" />
            <CopyableKV k="memory_chain_pass" v={String(rtCtx.memory_chain_pass ?? false)} vClass={rtCtx.memory_chain_pass ? 'text-obs-pass' : 'text-obs-hold'} />
            <CopyableKV k="local_records" v={String(rtCtx.local_records_count ?? 0)} />
            <CopyableKV k="text_excerpt_records" v={String(rtCtx.text_excerpt_records_count ?? 0)} />
            <CopyableKV k="decision_authority" v="KX108_ONLY" vClass="text-obs-kernel" />
          </div>
        </div>
      )}
      {projMem && (
        <div>
          <SectionTitle>Project Memory</SectionTitle>
          <div className="obs-card p-2.5 space-y-0.5 border-obs-memory/20 bg-obs-memory/5">
            <CopyableKV k="status" v={String(projMem.status ?? '—')} vClass={String(projMem.status ?? '').includes('PASS') ? 'text-obs-pass' : 'text-obs-hold'} />
            <CopyableKV k="local_records" v={String(projMem.local_records_count ?? projMem.graphiti_index_item_count ?? 0)} />
            <CopyableKV k="text_excerpts" v={String(projMem.text_excerpt_records_count ?? 0)} />
            <CopyableKV k="usable_material" v={String(projMem.usable_material ?? false)} vClass={projMem.usable_material ? 'text-obs-pass' : 'text-obs-hold'} />
            <CopyableKV k="material_status" v={String(projMem.contextual_material_status ?? '—')} />
          </div>
        </div>
      )}
      {candMem && (
        <div>
          <SectionTitle>Candidate Memory</SectionTitle>
          <div className="obs-card p-2.5 space-y-0.5 border-obs-hold/20 bg-obs-hold/5">
            <CopyableKV k="status" v={String(candMem.status ?? '—')} vClass={String(candMem.status ?? '').includes('READY') ? 'text-obs-pass' : 'text-obs-hold'} />
            <CopyableKV k="presave" v={String(candMem.presave_buffer_found ?? false)} />
            <CopyableKV k="auto_triage" v={String(candMem.auto_triage_found ?? false)} />
            <CopyableKV k="can_prepare" v={String(candMem.can_prepare_candidate ?? false)} vClass="text-obs-pass" />
            <CopyableKV k="can_commit" v="false" vClass="text-obs-block" />
            <CopyableKV k="memory_write" v="false" vClass="text-obs-block" />
          </div>
        </div>
      )}
      {opLoop && (
        <div>
          <SectionTitle>Operator Loop</SectionTitle>
          <div className="obs-card p-2.5 space-y-0.5 border-obs-block/20 bg-obs-block/5">
            <CopyableKV k="status" v={String(opLoop.status ?? '—')} vClass={String(opLoop.status ?? '').includes('PASS') ? 'text-obs-pass' : 'text-obs-hold'} />
            <CopyableKV k="brody_execute_allowed" v="false" vClass="text-obs-block" />
            <CopyableKV k="emits_act" v="false" vClass="text-obs-block" />
          </div>
        </div>
      )}
      {treePol && (
        <div>
          <SectionTitle>Tree Policy (34 arbres)</SectionTitle>
          <div className="obs-card p-2.5 space-y-0.5 border-obs-pass/20 bg-obs-pass/5">
            <CopyableKV k="status" v={String(treePol.status ?? '—')} vClass={String(treePol.status ?? '').includes('READY') ? 'text-obs-pass' : 'text-obs-hold'} />
            <CopyableKV k="safe_trees" v={String(treePol.safe_trees ?? 0)} vClass="text-obs-pass" />
            <CopyableKV k="blocked_action" v={String(treePol.blocked_action ?? 0)} vClass="text-obs-block" />
            <CopyableKV k="blocked_memory" v={String(treePol.blocked_memory ?? 0)} vClass="text-obs-hold" />
            <CopyableKV k="total" v={String(treePol.total_trees ?? 34)} />
          </div>
        </div>
      )}
      {temporal && (
        <div>
          <SectionTitle>Temporal Context</SectionTitle>
          <div className="obs-card p-2.5 space-y-0.5 border-obs-brody/20 bg-obs-brody/5">
            <CopyableKV k="status" v={String(temporal.status ?? '—')} vClass={String(temporal.status ?? '').includes('PASS') ? 'text-obs-pass' : 'text-obs-hold'} />
            <CopyableKV k="topic" v={String((temporal.present_context as Record<string,unknown>)?.current_topic ?? '—')} vClass="text-obs-memory" />
            <CopyableKV k="memory_chain" v={String((temporal.present_context as Record<string,unknown>)?.memory_chain_status ?? '—')} />
          </div>
        </div>
      )}
      {cogMod && (
        <div>
          <SectionTitle>Cognitive Modules</SectionTitle>
          <div className="obs-card p-2.5 space-y-0.5 border-obs-proof/20 bg-obs-proof/5">
            <CopyableKV k="status" v={String(cogMod.status ?? '—')} vClass={String(cogMod.status ?? '').includes('PASS') ? 'text-obs-pass' : 'text-obs-hold'} />
            <CopyableKV k="total_known" v={String(cogMod.total_known ?? 0)} />
            <CopyableKV k="modules_found" v={String(cogMod.modules_found ?? 0)} vClass="text-obs-pass" />
            {Array.isArray(cogMod.modules_active) && cogMod.modules_active.length > 0 && (
              <div className="pt-0.5">
                <div className="text-obs-dtext text-[9px] font-mono mb-0.5">active</div>
                <div className="flex flex-wrap gap-1">
                  {(cogMod.modules_active as string[]).slice(0, 6).map((m: string) => (
                    <span key={m} className="obs-badge-pass text-[8px]">{m}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      {liveCtx && Object.keys(liveCtx).length > 0 && (
        <div>
          <SectionTitle>Context Packet — Live</SectionTitle>
          <div className="obs-card p-3 space-y-0.5 border-obs-pass/20 bg-obs-pass/5">
            {Object.entries(liveCtx).slice(0, 12).map(([k, v]) => (
              <CopyableKV key={k} k={k} v={typeof v === 'object' ? JSON.stringify(v) : String(v ?? '')} />
            ))}
          </div>
        </div>
      )}
      <div>
        <SectionTitle>Context Packet</SectionTitle>
        <div className="obs-card p-3 space-y-0.5">
          <CopyableKV k="packet_id" v={cp.packet_id} vClass="text-obs-brody" />
          <CopyableKV k="query" v={cp.query} vClass="text-obs-text" />
          <CopyableKV k="language" v={cp.language} />
          <CopyableBool k="readonly" v={cp.readonly} />
          <CopyableBool k="context_signal_only" v={cp.context_signal_only} />
          <CopyableKV k="decision_authority" v={cp.decision_authority} vClass="text-obs-kernel" />
          <CopyableBool k="allowed_to_decide" v={cp.allowed_to_decide} />
          <CopyableBool k="allowed_to_act" v={cp.allowed_to_act} />
          <CopyableBool k="kernel_mutation" v={cp.kernel_mutation} />
          <CopyableBool k="memory_write" v={cp.memory_write} />
          <CopyableKV k="v18_hash_status" v={v18} vClass={v18 === 'PASS' ? 'text-obs-pass' : 'text-obs-block'} />
          <CopyableKV k="git_branch" v="ci-strict-sigma" vClass="text-obs-brody" />
        </div>
      </div>
      <div>
        <div className="flex items-center justify-between mb-1">
          <SectionTitle>Context Items</SectionTitle>
          <button onClick={() => onSendPrompt?.('Analyse le context packet dans le contexte kernel')} className="text-obs-dtext hover:text-obs-brody p-0.5" title="Send to Brody">
            <RefreshCw size={9} />
          </button>
        </div>
        <div className="obs-card p-3 space-y-1">
          {cp.context_items.map((item, i) => (
            <CopyableKV key={i} k={`${i + 1}`} v={item} />
          ))}
        </div>
      </div>
      <div>
        <SectionTitle>Dominant Trees ({cp.dominant_trees.length})</SectionTitle>
        <div className="obs-card p-3 flex flex-wrap gap-1">
          {cp.dominant_trees.map(t => (
            <button key={t} onClick={() => onSendPrompt?.(`Analyse tree_${t} dans le contexte kernel`)} className="obs-badge-memory cursor-pointer hover:bg-obs-memory/20 transition-colors" title={`Send analysis request for tree_${t}`}>
              tree_{t}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function GovernanceTab() {
  const os3 = MOCK_OS3_TICKET; const svt = MOCK_SOVEREIGN_TICKET; const wcs = MOCK_WORLD_CALLS
  const wccColor = (c: string) => c.includes('FORBIDDEN') ? 'text-obs-block' : c.includes('READ') ? 'text-obs-pass' : 'text-obs-hold'
  return (
    <div className="space-y-4">
      <div><SectionTitle>OS3 Proof Ticket</SectionTitle>
        <div className="obs-card p-3 space-y-0.5">
          <CopyableKV k="ticket_id" v={os3.ticket_id} vClass="text-obs-proof" />
          <CopyableKV k="status" v={os3.status} vClass={os3.status === 'PROOF_VALID' ? 'text-obs-pass' : 'text-obs-hold'} />
          <CopyableKV k="lean_ref" v={os3.lean_ref} vClass="text-obs-proof" />
          <CopyableKV k="tla_ref" v={os3.tla_ref} vClass="text-obs-proof" />
          <CopyableKV k="merkle_hash" v={os3.merkle_hash} />
          <CopyableBool k="os3_proves" v={os3.os3_proves} />
        </div>
      </div>
      <div><SectionTitle>Sovereign Ticket</SectionTitle>
        <div className="obs-card p-3 space-y-0.5">
          <CopyableKV k="ticket_id" v={svt.ticket_id} vClass="text-obs-kernel" />
          <CopyableKV k="authorized_by" v={svt.authorized_by} vClass="text-obs-kernel" />
          <CopyableBool k="dry_run_only" v={svt.dry_run_only} />
          <CopyableBool k="real_action_blocked" v={svt.real_action_blocked} />
        </div>
      </div>
      <div><SectionTitle>WorldCall / Gateway</SectionTitle>
        <div className="space-y-1.5">{wcs.map(wc => (
          <div key={wc.event_id} className="obs-card p-2.5">
            <div className="flex items-center justify-between mb-1"><span className={`text-[10px] font-mono font-semibold ${wccColor(wc.world_call_class)}`}>{wc.world_call_class}</span><span className={`obs-badge text-[9px] ${wc.gateway_result === 'ALLOW' ? 'obs-badge-pass' : 'obs-badge-block'}`}>{wc.gateway_result}</span></div>
            <p className="text-obs-mtext text-[10px] font-mono">{wc.action_description}</p>
            <div className="flex gap-3 mt-1"><span className="text-obs-dtext text-[9px] font-mono">dry_run: <span className="text-obs-pass">true</span></span><span className="text-obs-dtext text-[9px] font-mono">real_action: <span className="text-obs-block">false</span></span></div>
          </div>
        ))}</div>
      </div>
    </div>
  )
}

function MemoryTab() {
  const statusColor = (s: string) => ({ CANDIDATE_ONLY: 'obs-badge-memory', NEEDS_REVIEW: 'obs-badge-hold', PROMOTION_READY: 'obs-badge-proof', REJECTED: 'obs-badge-block', FROZEN: 'obs-badge-muted' }[s] ?? 'obs-badge-muted')
  return (
    <div className="space-y-4">
      <div><SectionTitle>Memory Candidates — Human Review Required</SectionTitle>
        <div className="space-y-2">{MOCK_MEMORY_CANDIDATES.map(mc => (
          <div key={mc.candidate_id} className="obs-card p-3">
            <div className="flex items-center justify-between mb-2"><CopyableKV k="id" v={mc.candidate_id} /><span className={statusColor(mc.status)}>{mc.status}</span></div>
            <p className="text-obs-mtext text-[10px] font-mono mb-2">{mc.content_summary}</p>
            <div className="flex gap-2 flex-wrap"><span className="obs-badge-memory">{mc.source_type}</span><span className="text-obs-dtext text-[9px] font-mono">write=<span className="text-obs-block">false</span></span></div>
          </div>
        ))}</div>
      </div>
      <div><SectionTitle>Graphiti Status</SectionTitle>
        <div className="obs-card p-3 space-y-0.5">
          <CopyableKV k="mode" v="READONLY BRIDGE" vClass="text-obs-pass" />
          <CopyableBool k="neo4j_write" v={false} />
          <CopyableBool k="graphiti_write" v={false} />
          <CopyableKV k="decision_authority" v="KX108_ONLY" vClass="text-obs-kernel" />
        </div>
      </div>
    </div>
  )
}

function GencoinTab() {
  return (
    <div className="space-y-4">
      <div className="obs-card p-3 border-obs-gencoin/20 bg-obs-gencoin/5">
        <div className="text-[9px] font-mono text-obs-gencoin font-bold mb-1">⚠ GENCOIN IS NOT A REAL TOKEN</div>
        <div className="text-[10px] font-mono text-obs-mtext">Ledger only. No smart contract. No wallet. No mint. Post-proof symbolic valuation only.</div>
      </div>
      <div><SectionTitle>Ledger Entries</SectionTitle>
        <div className="space-y-2">{MOCK_GENCOIN.map(gc => (
          <div key={gc.entry_id} className="obs-card p-3">
            <div className="flex items-center justify-between mb-1.5"><span className="text-obs-gencoin font-mono text-sm font-semibold">{gc.amount_symbolic} GC</span><span className="obs-badge-gencoin">LEDGER ONLY</span></div>
            <p className="text-obs-mtext text-[10px] font-mono mb-2">{gc.description}</p>
            <div className="space-y-0.5"><CopyableKV k="proof_ref" v={gc.proof_ref} vClass="text-obs-proof" /><CopyableBool k="is_real_token" v={gc.is_real_token} /><CopyableBool k="post_proof_only" v={gc.post_proof_only} /><CopyableBool k="ledger_only" v={gc.ledger_only} /></div>
          </div>
        ))}</div>
      </div>
    </div>
  )
}

function AuditTab({ live }: { live?: Record<string, unknown> }) {
  const resultBadge = (r: string) => ({ OK: 'obs-badge-pass', BLOCKED: 'obs-badge-block', DRY_RUN: 'obs-badge-hold', HOLD: 'obs-badge-hold' }[r] ?? 'obs-badge-muted')
  const typeColor: Record<string, string> = { context_read: 'text-obs-memory', brody_response: 'text-obs-brody', memory_candidate: 'text-obs-memory', governance_check: 'text-obs-kernel', world_call: 'text-obs-world', gencoin_entry: 'text-obs-gencoin' }
  const [showMd, setShowMd] = useState(false)
  const responseMd = live?.response_md as string | undefined
  return (
    <div className="space-y-4">
      {responseMd && (
        <div>
          <div className="flex items-center justify-between mb-1">
            <SectionTitle>response_md — Local Engine Audit</SectionTitle>
            <button onClick={() => setShowMd(v => !v)} className="text-[9px] font-mono text-obs-dtext hover:text-obs-brody px-1 border border-obs-border/40 rounded">
              {showMd ? 'hide' : 'show'}
            </button>
          </div>
          {showMd && (
            <pre className="obs-card p-3 text-[9px] font-mono text-obs-mtext whitespace-pre-wrap break-words max-h-64 overflow-y-auto">
              {responseMd}
            </pre>
          )}
          {!showMd && (
            <div className="obs-card p-2 text-[9px] font-mono text-obs-dtext truncate">{responseMd.slice(0, 80)}…</div>
          )}
        </div>
      )}
      <div className="obs-card p-2 border-obs-dtext/20"><div className="text-[9px] font-mono text-obs-dtext">Append-only audit trail. WorldActionBus. Read-only replay.</div></div>
      <div className="space-y-1">{MOCK_AUDIT.map(ev => (
        <div key={ev.event_id} className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-obs-muted/30 transition-colors">
          <span className={`text-[9px] font-mono ${typeColor[ev.type] ?? 'text-obs-mtext'} w-28 shrink-0`}>{ev.type}</span>
          <span className="text-obs-mtext text-[10px] font-mono flex-1 truncate">{ev.description}</span>
          <span className={`shrink-0 ${resultBadge(ev.result)}`}>{ev.result}</span>
          <span className="text-obs-dtext text-[9px] font-mono shrink-0">{new Date(ev.timestamp).toLocaleTimeString()}</span>
        </div>
      ))}</div>
    </div>
  )
}

function ZoneBadge({ zone }: { zone?: string }) {
  if (!zone || zone === 'NOT_RUN') return <span className="obs-badge-muted text-[8px]">NOT_RUN</span>
  if (zone === 'CRISTAL') return <span className="obs-badge-pass text-[8px]">CRISTAL</span>
  if (zone === 'TRANSITION') return <span className="obs-badge-hold text-[8px]">TRANSITION</span>
  return <span className="obs-badge-block text-[8px]">NEANT</span>
}

function AutomationTab({ snap }: { snap?: AutomationSnapshot }) {
  if (!snap) return (
    <div className="obs-card p-3 text-obs-dtext text-[10px] font-mono">
      No automation snapshot — send a message first.
    </div>
  )

  const ledger = snap.session_ledger
  const presave = snap.presave_buffer
  const triage = snap.auto_triage
  const pipeline = snap.memory_candidate_pipeline
  const opLoop = snap.operator_loop
  const next = snap.next_allowed_steps ?? []
  const blocked = snap.blocked_steps ?? []

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="obs-card p-2.5 border-obs-brody/20 bg-obs-brody/5">
        <CopyableKV k="request_type" v={snap.request_type ?? '—'} vClass="text-obs-brody" />
        <CopyableKV k="decision_authority" v="KX108_ONLY" vClass="text-obs-kernel" />
        <CopyableBool k="readonly" v={true} />
        <CopyableBool k="emits_act" v={false} />
        <CopyableBool k="graphiti_write" v={false} />
        <CopyableBool k="neo4j_write" v={false} />
      </div>

      {/* Session Ledger */}
      <div>
        <SectionTitle>Session Ledger</SectionTitle>
        <div className="obs-card p-2.5 space-y-0.5">
          <CopyableKV k="status" v={ledger?.status ?? '—'} vClass={ledger?.enabled ? 'text-obs-pass' : 'text-obs-dtext'} />
          <CopyableKV k="event_candidate_created" v={String(ledger?.event_candidate_created ?? false)} vClass={ledger?.event_candidate_created ? 'text-obs-pass' : 'text-obs-dtext'} />
          {ledger?.event_hash && <CopyableKV k="event_hash" v={ledger.event_hash.slice(0, 16) + '…'} />}
          {ledger?.sequence !== undefined && <CopyableKV k="sequence" v={String(ledger.sequence)} />}
          <CopyableBool k="memory_write" v={false} />
        </div>
      </div>

      {/* Presave Buffer */}
      <div>
        <SectionTitle>Presave Buffer</SectionTitle>
        <div className="obs-card p-2.5 space-y-0.5">
          <CopyableKV k="status" v={presave?.status ?? 'NOT_APPLICABLE'} vClass={presave?.enabled ? 'text-obs-hold' : 'text-obs-dtext'} />
          <CopyableKV k="manual_validation_required" v="true" vClass="text-obs-hold" />
        </div>
      </div>

      {/* Auto Triage */}
      <div>
        <SectionTitle>Auto Triage</SectionTitle>
        <div className="obs-card p-2.5 space-y-0.5">
          <div className="flex items-center gap-2 py-0.5">
            <span className="text-obs-dtext font-mono text-[10px] shrink-0 w-32">zone</span>
            <ZoneBadge zone={triage?.zone} />
          </div>
          <CopyableKV k="status" v={triage?.status ?? '—'} vClass={triage?.enabled ? 'text-obs-pass' : 'text-obs-dtext'} />
          <CopyableBool k="memory_intake" v={false} />
          {triage?.axes && triage.axes.length > 0 && (
            <div className="pt-0.5">
              <div className="text-obs-dtext text-[9px] font-mono mb-0.5">axes</div>
              <div className="flex flex-wrap gap-1">
                {triage.axes.map(a => <span key={a} className="obs-badge-memory text-[8px]">{a}</span>)}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Memory Candidate Pipeline */}
      <div>
        <SectionTitle>Memory Pipeline</SectionTitle>
        <div className="obs-card p-2.5 space-y-0.5">
          <CopyableKV k="review_gate_status" v={pipeline?.review_gate_status ?? 'NOT_APPLICABLE'} vClass={pipeline?.needs_review ? 'text-obs-hold' : 'text-obs-dtext'} />
          <CopyableKV k="gates_passing" v={`${pipeline?.gates_passing ?? 0}/${pipeline?.gates_total ?? 6}`} />
          <CopyableBool k="graphiti_write" v={false} />
          <CopyableBool k="neo4j_write" v={false} />
        </div>
      </div>

      {/* Operator Loop */}
      <div>
        <SectionTitle>Operator Loop</SectionTitle>
        <div className="obs-card p-2.5 space-y-0.5">
          <CopyableKV k="command_gate_classification" v={opLoop?.command_gate_classification ?? 'NOT_APPLICABLE'} vClass={opLoop?.human_command_packet_ready ? 'text-obs-hold' : 'text-obs-dtext'} />
          <CopyableKV k="human_operator_required" v={String(opLoop?.human_operator_required ?? false)} vClass={opLoop?.human_operator_required ? 'text-obs-hold' : 'text-obs-dtext'} />
          <CopyableBool k="execution_allowed_for_brody" v={false} />
        </div>
      </div>

      {/* Next / Blocked */}
      {next.length > 0 && (
        <div>
          <SectionTitle>Next Allowed Steps</SectionTitle>
          <div className="obs-card p-2.5 flex flex-wrap gap-1">
            {next.slice(0, 8).map(s => <span key={s} className="obs-badge-pass text-[8px]">{s.replace(/_/g, ' ')}</span>)}
            {next.length > 8 && <span className="text-obs-dtext text-[8px] font-mono">+{next.length - 8}</span>}
          </div>
        </div>
      )}
      {blocked.length > 0 && (
        <div>
          <SectionTitle>Blocked Steps</SectionTitle>
          <div className="obs-card p-2.5 flex flex-wrap gap-1">
            {blocked.slice(0, 8).map(s => <span key={s} className="obs-badge-block text-[8px]">{s.replace(/_/g, ' ')}</span>)}
            {blocked.length > 8 && <span className="text-obs-dtext text-[8px] font-mono">+{blocked.length - 8}</span>}
          </div>
        </div>
      )}
    </div>
  )
}

function MaterialBadge({ status }: { status?: string }) {
  if (!status || status === 'CHAIN_UNAVAILABLE') return <span className="obs-badge-muted text-[8px]">OFFLINE</span>
  if (status === 'HAS_MATERIAL') return <span className="obs-badge-pass text-[8px]">HAS_MATERIAL</span>
  if (status === 'PARTIAL_MATERIAL') return <span className="obs-badge-warn text-[8px]">PARTIAL</span>
  if (status === 'LOW_MATERIAL') return <span className="obs-badge-warn text-[8px]">LOW_MATERIAL</span>
  return <span className="obs-badge-muted text-[8px]">{status}</span>
}

function StageBadge({ stage }: { stage?: string }) {
  if (!stage) return null
  if (stage === 'PASS') return <span className="obs-badge-pass text-[8px]">PASS</span>
  if (stage === 'PARTIAL' || stage === 'TERMINAL_FALLBACK') return <span className="obs-badge-warn text-[8px]">{stage}</span>
  return <span className="obs-badge-block text-[8px]">{stage}</span>
}

function FreezeMetricsTab({ snap }: { snap?: FreezeMetricsSnapshot }) {
  if (!snap) return (
    <div className="obs-card p-3 text-obs-dtext text-[10px] font-mono">
      No freeze_metrics_snapshot — send a message first.
    </div>
  )
  const chain = snap.context_packet_chain
  const mem = snap.memory_pipeline
  const op = snap.operator_loop
  const x108 = snap.x108_boundary
  const llm = snap.runtime_llm
  const x108proof = snap.x108_proof_state
  const notFound = snap.not_found_in_freeze_sources ?? {}

  return (
    <div className="space-y-3 text-[10px] font-mono">
      {/* Header */}
      <div className="obs-card p-2.5 border-obs-kernel/20 bg-obs-kernel/5">
        <CopyableKV k="source_mode" v={snap.source_mode ?? '—'} vClass="text-obs-kernel" />
        <CopyableKV k="status" v={snap.status ?? '—'} vClass="text-obs-pass" />
        <CopyableKV k="pointer_files" v={String(snap.pointer_file_count ?? 0)} />
        <CopyableKV k="decision_authority" v="KX108_ONLY" vClass="text-obs-kernel" />
      </div>

      {/* ContextPacket Chain */}
      <div>
        <SectionTitle>ContextPacket Chain</SectionTitle>
        <div className="obs-card p-2.5 space-y-0.5">
          <CopyableKV k="chain_status" v={chain?.status ?? '—'} vClass={chain?.status === 'CHAIN_PASS' ? 'text-obs-pass' : 'text-obs-warn'} />
          <CopyableKV k="query" v={chain?.query ?? '—'} />
          <CopyableKV k="consumer" v={chain?.consumer ?? '—'} />
          <CopyableKV k="engine" v={chain?.engine ?? '—'} />
          <CopyableKV k="hydration" v={chain?.hydration ?? '—'} />
        </div>
      </div>

      {/* Operator Loop */}
      <div>
        <SectionTitle>Operator Loop</SectionTitle>
        <div className="obs-card p-2.5 space-y-0.5">
          <CopyableKV k="status" v={op?.status ?? '—'} vClass={op?.status?.includes('PASS') ? 'text-obs-pass' : 'text-obs-warn'} />
          <CopyableKV k="command_gate" v={op?.command_gate ?? '—'} />
          <CopyableKV k="execution_receipt" v={op?.execution_receipt ?? '—'} />
          <CopyableKV k="handoff_line" v={op?.handoff_line ?? '—'} />
          <CopyableKV k="final_baseline" v={op?.final_baseline ?? '—'} />
          <CopyableBool k="brody_execute_allowed" v={op?.brody_execute_allowed ?? false} />
          <CopyableBool k="human_operator_required" v={op?.human_operator_required ?? true} />
        </div>
      </div>

      {/* Memory Pipeline */}
      <div>
        <SectionTitle>Memory Pipeline</SectionTitle>
        <div className="obs-card p-2.5 space-y-0.5">
          <CopyableKV k="session_ledger" v={mem?.session_ledger ?? '—'} />
          <CopyableKV k="presave_buffer" v={mem?.presave_buffer ?? '—'} />
          <CopyableKV k="auto_triage" v={mem?.auto_triage ?? '—'} />
          <CopyableKV k="graphiti_apply" v={mem?.graphiti_import_apply ?? '—'} />
          <CopyableBool k="memory_write" v={mem?.memory_write ?? false} />
          <CopyableBool k="graphiti_write" v={mem?.graphiti_write ?? false} />
          <CopyableBool k="neo4j_write" v={mem?.neo4j_write ?? false} />
        </div>
      </div>

      {/* X108 Boundary */}
      <div>
        <SectionTitle>X108 Boundary</SectionTitle>
        <div className="obs-card p-2.5 space-y-0.5">
          <CopyableKV k="decision_authority" v={x108?.decision_authority ?? 'KX108_ONLY'} vClass="text-obs-kernel" />
          <CopyableBool k="emits_act" v={x108?.emits_act ?? false} />
          <CopyableBool k="emits_verdict" v={x108?.emits_verdict ?? false} />
          <CopyableBool k="kernel_mutation" v={x108?.kernel_mutation ?? false} />
        </div>
      </div>

      {/* Runtime LLM */}
      <div>
        <SectionTitle>Runtime LLM</SectionTitle>
        <div className="obs-card p-2.5 space-y-0.5">
          <CopyableBool k="brody_llm_obsidien" v={llm?.brody_llm_obsidien ?? false} />
          <CopyableBool k="runtime_freeze" v={llm?.runtime_freeze ?? false} />
          <CopyableBool k="boundary_ok" v={llm?.boundary_ok ?? false} />
          <CopyableBool k="detector_ok" v={llm?.detector_ok ?? false} />
        </div>
      </div>

      {/* X108 Proof State */}
      <div>
        <SectionTitle>X108 Proof State</SectionTitle>
        <div className="obs-card p-2.5 space-y-0.5">
          <CopyableKV k="status" v={x108proof?.status ?? '—'} />
          <CopyableKV k="pointers_checked" v={x108proof?.checked_pointer_count ?? '—'} />
          <CopyableBool k="dry_run" v={x108proof?.dry_run ?? true} />
        </div>
      </div>

      {/* NOT_FOUND */}
      {Object.keys(notFound).length > 0 && (
        <div>
          <SectionTitle>NOT FOUND IN FREEZE SOURCES</SectionTitle>
          <div className="obs-card p-2.5 space-y-0.5">
            {Object.entries(notFound).slice(0, 12).map(([k, v]) => (
              <CopyableKV key={k} k={k} v={v} vClass="text-obs-warn" />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function StructuredResponseTab({ snap }: { snap?: StructuredResponseSnapshot }) {
  if (!snap) return (
    <div className="obs-card p-3 text-obs-dtext text-[10px] font-mono">
      No structured_response_snapshot yet. Send a message first.
    </div>
  )
  const hasMaterial = snap.text_material_status === 'HAS_MATERIAL' || snap.text_material_status === 'PARTIAL_MATERIAL'
  return (
    <div className="space-y-3 text-[10px] font-mono">
      <div className="obs-card p-2.5 space-y-1">
        <SectionTitle>Chain Status</SectionTitle>
        <div className="flex items-center gap-2 py-0.5">
          <span className="text-obs-dtext shrink-0 w-24">material</span>
          <MaterialBadge status={snap.text_material_status} />
        </div>
        <CopyableKV k="status" v={snap.status} vClass={snap.status?.includes('PASS') ? 'text-obs-pass' : 'text-obs-warn'} />
        <CopyableKV k="items_count" v={String(snap.context_items_count ?? 0)} />
        <CopyableKV k="memory_query" v={snap.memory_query ?? '—'} />
        <CopyableKV k="graphiti_status" v={snap.graphiti_status ?? '—'} />
        {snap.graphiti_blocker && <CopyableKV k="blocker" v={snap.graphiti_blocker} vClass="text-obs-warn" />}
      </div>
      <div className="obs-card p-2.5 space-y-1">
        <SectionTitle>Chain Stages</SectionTitle>
        <div className="flex items-center gap-2 py-0.5">
          <span className="text-obs-dtext shrink-0 w-24">query</span>
          <StageBadge stage={snap.query_stage} />
        </div>
        <div className="flex items-center gap-2 py-0.5">
          <span className="text-obs-dtext shrink-0 w-24">consumer</span>
          <StageBadge stage={snap.consumer_stage} />
        </div>
        <div className="flex items-center gap-2 py-0.5">
          <span className="text-obs-dtext shrink-0 w-24">engine</span>
          <StageBadge stage={snap.engine_stage} />
        </div>
      </div>
      {hasMaterial && snap.response_md && (
        <div className="obs-card p-2.5 space-y-1">
          <SectionTitle>Chain Response</SectionTitle>
          <pre className="text-obs-text text-[9px] whitespace-pre-wrap break-words max-h-48 overflow-y-auto">{snap.response_md.slice(0, 600)}{snap.response_md.length > 600 ? '…' : ''}</pre>
        </div>
      )}
      {snap.source_doc_refs && snap.source_doc_refs.length > 0 && (
        <div className="obs-card p-2.5 space-y-1">
          <SectionTitle>Source Docs</SectionTitle>
          {snap.source_doc_refs.map(ref => (
            <div key={ref} className="text-obs-dtext text-[9px] truncate">{ref}</div>
          ))}
        </div>
      )}
    </div>
  )
}

interface RightPanelProps { onSendPrompt?: (text: string) => void; lastBackendPayload?: Record<string, unknown> }

export function RightPanel({ onSendPrompt, lastBackendPayload }: RightPanelProps) {
  const [activeTab, setActiveTab] = useState<TabId>('context')
  const automationSnap = lastBackendPayload?.automation_snapshot as AutomationSnapshot | undefined
  const structuredSnap = lastBackendPayload?.structured_response_snapshot as StructuredResponseSnapshot | undefined
  const freezeSnap = lastBackendPayload?.freeze_metrics_snapshot as FreezeMetricsSnapshot | undefined

  const TAB_CONTENT: Record<TabId, React.ReactNode> = {
    context:    <ContextTab onSendPrompt={onSendPrompt} live={lastBackendPayload} />,
    governance: <GovernanceTab />,
    memory:     <MemoryTab />,
    gencoin:    <GencoinTab />,
    audit:      <AuditTab live={lastBackendPayload} />,
    automation: (
      <div className="space-y-4">
        <StructuredResponseTab snap={structuredSnap} />
        <AutomationTab snap={automationSnap} />
      </div>
    ),
    backend:    <BackendStatusPanel />,
    freeze:     <FreezeMetricsTab snap={freezeSnap} />,
  }

  return (
    <div className="w-[360px] bg-obs-surface border-l border-obs-border flex flex-col overflow-hidden shrink-0">
      <div className="flex items-center gap-0.5 px-2 py-2 border-b border-obs-border shrink-0">
        {TABS.map(tab => {
          const Icon = tab.icon; const active = activeTab === tab.id
          return (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center gap-1 px-2 py-1 rounded text-[10px] font-mono font-semibold transition-colors ${active ? 'bg-obs-border text-obs-text' : 'text-obs-dtext hover:text-obs-mtext'}`}>
              <Icon size={9} />{tab.label}
            </button>
          )
        })}
      </div>
      <div className="flex-1 overflow-y-auto p-3">{TAB_CONTENT[activeTab]}</div>
    </div>
  )
}
