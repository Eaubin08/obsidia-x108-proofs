import { useState } from 'react'
import { Send, ArrowRight } from 'lucide-react'
import type { TranslationTrace } from '../types/translation'
import { runOSTradPipeline } from '../lib/osTradPipeline'
import type { DetectedLanguage } from '../lib/language'

interface Props {
  sessionLanguage: DetectedLanguage
}

function UnitBadge({ symbol, label, role }: { symbol: string; label: string; role: string }) {
  const cls = {
    INTENT:     'bg-obs-brody/10 text-obs-brody border-obs-brody/20',
    ENTITY:     'bg-obs-memory/10 text-obs-memory border-obs-memory/20',
    QUALIFIER:  'bg-obs-block/10 text-obs-block border-obs-block/20',
    CONSTRAINT: 'bg-obs-pass/10 text-obs-pass border-obs-pass/20',
    UNKNOWN:    'bg-obs-muted/20 text-obs-dtext border-obs-border/20',
  }[role] ?? 'bg-obs-muted/20 text-obs-dtext border-obs-border/20'
  return (
    <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono border ${cls}`}>
      {symbol} {label} <span className="opacity-60">({role})</span>
    </span>
  )
}

function PipelineStep({ n, label, content, statusCls }: { n: number; label: string; content: string; statusCls?: string }) {
  return (
    <div className="flex gap-3">
      <div className="flex flex-col items-center gap-1 shrink-0">
        <div className="w-6 h-6 rounded-full bg-obs-muted/40 border border-obs-border flex items-center justify-center text-[9px] font-mono text-obs-dtext">{n}</div>
        <div className="w-px flex-1 bg-obs-border/40 min-h-[8px]" />
      </div>
      <div className="pb-3 flex-1">
        <div className="text-[10px] font-mono text-obs-dtext mb-0.5">{label}</div>
        <div className={`text-[10px] font-mono ${statusCls ?? 'text-obs-mtext'}`}>{content}</div>
      </div>
    </div>
  )
}

export function TranslationView({ sessionLanguage }: Props) {
  const [input, setInput] = useState('')
  const [trace, setTrace] = useState<TranslationTrace | null>(null)

  const run = () => {
    const t = input.trim()
    if (!t) return
    setTrace(runOSTradPipeline(t, sessionLanguage))
  }

  const ir = trace?.ir_candidate

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      <div className="flex items-center gap-2">
        <ArrowRight size={13} className="text-obs-proof" />
        <span className="text-obs-text font-mono text-sm font-semibold">OS Trad / IR / OS Reverse</span>
      </div>

      <div className="rounded-lg border border-obs-proof/20 bg-obs-proof/5 p-3 text-[9px] font-mono text-obs-mtext space-y-0.5">
        <div className="text-obs-proof font-semibold mb-1">TRANSLATION PIPELINE</div>
        <div>Natural input → OS Trad → Alphabet → IR Candidate → OS Reverse → X-108 boundary</div>
        <div className="mt-1 text-obs-dtext">OS Trad ne décide pas · IR ne décide pas · OS Reverse ne décide pas · X-108 reste autorité</div>
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') run() }}
          className="flex-1 bg-obs-surface border border-obs-border rounded-lg px-3 py-2 text-obs-text text-xs font-mono outline-none focus:border-obs-proof/50 transition-colors placeholder:text-obs-dtext"
          placeholder="Entrer une phrase naturelle à traduire..."
        />
        <button
          onClick={run}
          disabled={!input.trim()}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-obs-proof/20 border border-obs-proof/30 text-obs-proof text-xs font-mono hover:bg-obs-proof/30 disabled:opacity-30 transition-colors"
        >
          <Send size={11} /> RUN
        </button>
      </div>

      {trace && (
        <div className="space-y-4">
          {/* Trace header */}
          <div className="flex items-center gap-2 text-[9px] font-mono">
            <span className="text-obs-dtext">trace_id</span>
            <span className="text-obs-proof">{trace.trace_id}</span>
            <span className={`ml-auto px-1.5 py-0.5 rounded ${
              trace.os_trad_status === 'BLOCKED' ? 'bg-obs-block/10 text-obs-block' : 'bg-obs-pass/10 text-obs-pass'
            }`}>{trace.os_trad_status}</span>
            <span className="text-obs-hold">{trace.source}</span>
          </div>

          {/* Pipeline steps */}
          <div>
            <PipelineStep n={1} label="Natural Input" content={trace.user_input} statusCls="text-obs-text" />
            <PipelineStep n={2} label="OS Trad — Language Detection"
              content={`detected=${trace.detected_language} · response_lang=${trace.response_language}`} />
            <div className="flex gap-3 pb-3">
              <div className="flex flex-col items-center gap-1 shrink-0">
                <div className="w-6 h-6 rounded-full bg-obs-muted/40 border border-obs-border flex items-center justify-center text-[9px] font-mono text-obs-dtext">3</div>
                <div className="w-px flex-1 bg-obs-border/40 min-h-[8px]" />
              </div>
              <div className="pb-3 flex-1">
                <div className="text-[10px] font-mono text-obs-dtext mb-1">Symbolic Alphabet Units</div>
                {trace.alphabet_units.length > 0 ? (
                  <div className="flex flex-wrap gap-1">
                    {trace.alphabet_units.map((u, i) => <UnitBadge key={i} {...u} />)}
                  </div>
                ) : (
                  <span className="text-obs-dtext text-[9px] font-mono">no units extracted</span>
                )}
              </div>
            </div>
            <div className="flex gap-3 pb-3">
              <div className="flex flex-col items-center gap-1 shrink-0">
                <div className="w-6 h-6 rounded-full bg-obs-muted/40 border border-obs-border flex items-center justify-center text-[9px] font-mono text-obs-dtext">4</div>
                <div className="w-px flex-1 bg-obs-border/40 min-h-[8px]" />
              </div>
              {ir && (
                <div className="pb-3 flex-1 space-y-1">
                  <div className="text-[10px] font-mono text-obs-dtext mb-0.5">IR Candidate</div>
                  <div className="bg-obs-surface border border-obs-border rounded-lg p-2.5 text-[9px] font-mono space-y-0.5">
                    <div className="flex gap-2"><span className="text-obs-dtext w-24 shrink-0">ir_id</span><span className="text-obs-proof">{ir.ir_id}</span></div>
                    <div className="flex gap-2"><span className="text-obs-dtext w-24 shrink-0">intent_type</span><span className="text-obs-brody">{ir.intent_type}</span></div>
                    <div className="flex gap-2"><span className="text-obs-dtext w-24 shrink-0">action_candidate</span><span className={ir.action_candidate ? 'text-obs-hold' : 'text-obs-pass'}>{String(ir.action_candidate)}</span></div>
                    <div className="flex gap-2"><span className="text-obs-dtext w-24 shrink-0">allowed_to_decide</span><span className="text-obs-block">false</span></div>
                    <div className="flex gap-2"><span className="text-obs-dtext w-24 shrink-0">allowed_to_act</span><span className="text-obs-block">false</span></div>
                    <div className="flex gap-2"><span className="text-obs-dtext w-24 shrink-0">decision_authority</span><span className="text-obs-kernel">X108_ONLY</span></div>
                    {ir.risk_flags.length > 0 && (
                      <div className="flex gap-2 flex-wrap">
                        <span className="text-obs-dtext w-24 shrink-0">risk_flags</span>
                        <div className="flex gap-1 flex-wrap">
                          {ir.risk_flags.map(f => <span key={f} className="px-1 rounded bg-obs-block/10 text-obs-block">{f}</span>)}
                        </div>
                      </div>
                    )}
                    {ir.contradictions.length > 0 && (
                      <div>
                        {ir.contradictions.map(c => <div key={c} className="text-obs-hold">⚠ {c}</div>)}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            <PipelineStep n={5} label="Context Packet Reference"
              content={`context_packet_id=${trace.context_packet_id}`}
              statusCls="text-obs-memory" />
            <PipelineStep n={6} label="OS Reverse — Projection in User Language"
              content={trace.os_reverse_projection}
              statusCls="text-obs-text" />
            <div className="flex gap-3">
              <div className="shrink-0">
                <div className="w-6 h-6 rounded-full bg-obs-kernel/20 border border-obs-kernel/30 flex items-center justify-center text-[9px] font-mono text-obs-kernel">7</div>
              </div>
              <div className="flex-1">
                <div className="text-[10px] font-mono text-obs-dtext mb-0.5">X-108 Boundary</div>
                <div className="text-[10px] font-mono text-obs-kernel font-semibold">x108_boundary_status={trace.x108_boundary_status}</div>
                <div className="text-[9px] font-mono text-obs-dtext mt-0.5">
                  allowed_to_decide=<span className="text-obs-block">false</span> · allowed_to_act=<span className="text-obs-block">false</span> · memory_write=<span className="text-obs-block">false</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {!trace && (
        <div className="text-center text-obs-dtext text-[10px] font-mono py-12">
          Entrer une phrase pour lancer le pipeline OS Trad → IR → OS Reverse
        </div>
      )}
    </div>
  )
}
