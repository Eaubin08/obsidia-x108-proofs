import { useState, useEffect, useCallback } from 'react'
import { RefreshCw, ChevronDown, ChevronRight, GitBranch } from 'lucide-react'
import { getCognitiveTrees } from '../api/obsidiaClient'
import type { CognitiveTree } from '../api/obsidiaClient'

interface Props {
  onSendPrompt?: (text: string) => void
}

const DOMAIN_BADGE: Record<string, string> = {
  I_FONDAMENTAUX: 'obs-badge-muted',
  COGNITION:      'obs-badge-brody',
  EPISTEMICS:     'obs-badge-proof',
  SOCIAL:         'obs-badge-memory',
  PLANNING:       'obs-badge-hold',
  TEMPORAL:       'obs-badge-gencoin',
  GOVERNANCE:     'obs-badge-pass',
  META:           'obs-badge-muted',
  INFRASTRUCTURE: 'obs-badge-muted',
}

const DOMAIN_ORDER = [
  'I_FONDAMENTAUX', 'COGNITION', 'EPISTEMICS', 'SOCIAL',
  'PLANNING', 'TEMPORAL', 'GOVERNANCE', 'META', 'INFRASTRUCTURE',
]

function cleanName(raw: string): string {
  return raw.replace(/^ARBRE_\d+__/, '').replace(/_/g, ' ')
}

function groupByDomain(trees: CognitiveTree[]): Record<string, CognitiveTree[]> {
  const groups: Record<string, CognitiveTree[]> = {}
  for (const t of trees) {
    if (!groups[t.domain]) groups[t.domain] = []
    groups[t.domain].push(t)
  }
  return groups
}

export function TreeExplorer({ onSendPrompt }: Props) {
  const [trees, setTrees]         = useState<CognitiveTree[]>([])
  const [source, setSource]       = useState<'api' | 'mock'>('mock')
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState<string | null>(null)
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({})

  const fetchTrees = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await getCognitiveTrees()
      setTrees(result.data)
      setSource(result.source as 'api' | 'mock')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'fetch error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchTrees() }, [fetchTrees])

  const toggleDomain = (domain: string) =>
    setCollapsed(prev => ({ ...prev, [domain]: !prev[domain] }))

  const groups = groupByDomain(trees)
  const orderedDomains = DOMAIN_ORDER.filter(d => groups[d])

  return (
    <div className="space-y-3">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <GitBranch size={11} className="text-obs-brody" />
          <span className="text-obs-text text-[11px] font-mono font-semibold">
            TreeSpace R^34
          </span>
          {trees.length > 0 && (
            <span className="obs-badge-pass text-[8px]">{trees.length} arbres</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-[9px] font-mono ${source === 'api' ? 'text-obs-pass' : 'text-obs-hold'}`}>
            {source === 'api' ? 'REAL_BACKEND' : 'MOCK'}
          </span>
          <button
            onClick={fetchTrees}
            disabled={loading}
            className="text-obs-dtext hover:text-obs-brody disabled:opacity-40 transition-colors"
            title="Rafraîchir"
          >
            <RefreshCw size={11} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Sovereignty invariant */}
      <div className="obs-card px-2.5 py-1.5 border-obs-kernel/20 bg-obs-kernel/5">
        <span className="text-obs-dtext text-[9px] font-mono">
          context_signal_only=true · decision_authority=KX108_ONLY · emits_act=false
        </span>
      </div>

      {/* Error */}
      {error && (
        <div className="obs-card p-2 border-obs-block/30 bg-obs-block/5">
          <span className="text-obs-block text-[10px] font-mono">{error}</span>
        </div>
      )}

      {/* Empty / loading state */}
      {!loading && trees.length === 0 && !error && (
        <div className="obs-card p-3 text-obs-dtext text-[10px] font-mono">
          {source === 'mock'
            ? 'Backend hors-ligne — les 34 arbres sont disponibles via GET /api/periphery/cognitive/trees'
            : 'Aucun arbre retourné par le backend.'}
        </div>
      )}

      {/* Domain groups */}
      {orderedDomains.map(domain => {
        const domainTrees = groups[domain]
        const isOpen = !collapsed[domain]
        return (
          <div key={domain} className="obs-card overflow-hidden">
            {/* Domain header */}
            <button
              onClick={() => toggleDomain(domain)}
              className="w-full flex items-center gap-2 px-3 py-2 hover:bg-obs-muted/20 transition-colors"
            >
              {isOpen
                ? <ChevronDown size={10} className="text-obs-dtext shrink-0" />
                : <ChevronRight size={10} className="text-obs-dtext shrink-0" />}
              <span className={`text-[10px] font-mono font-semibold ${DOMAIN_BADGE[domain] ? '' : 'text-obs-mtext'}`}>
                <span className={DOMAIN_BADGE[domain] ?? 'obs-badge-muted'}>{domain}</span>
              </span>
              <span className="text-obs-dtext text-[9px] font-mono ml-auto">
                {domainTrees.length} arbres
              </span>
            </button>

            {/* Trees list */}
            {isOpen && (
              <div className="border-t border-obs-border/40">
                {domainTrees.map(tree => (
                  <div
                    key={tree.id}
                    className="flex items-center gap-2 px-3 py-1.5 hover:bg-obs-muted/10 transition-colors group"
                  >
                    <span className="text-obs-dtext text-[9px] font-mono w-6 shrink-0 text-right">
                      {tree.id}
                    </span>
                    <span className="text-obs-text text-[10px] font-mono flex-1 truncate" title={cleanName(tree.name)}>
                      {cleanName(tree.name)}
                    </span>
                    {onSendPrompt && (
                      <button
                        onClick={() => onSendPrompt(`Analyse l'arbre ${tree.id} (${cleanName(tree.name)}) dans le contexte kernel Obsidia`)}
                        className="shrink-0 opacity-0 group-hover:opacity-100 text-[9px] font-mono text-obs-brody hover:text-obs-brody/80 border border-obs-brody/30 rounded px-1.5 py-0.5 transition-all"
                        title="Interroger via Brody"
                      >
                        → Brody
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
