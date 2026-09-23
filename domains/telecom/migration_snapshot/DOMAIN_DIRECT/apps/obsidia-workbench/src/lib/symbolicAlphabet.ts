import type { AlphabetUnit } from '../types/translation'

const INTENT_RE   = /\b(autorise[rz]?|authorize?|execute?|executer?|run|lancer|faire|fais|do|allow|permit|permets?|décide[rz]?|decide?s?|go|start|créer|create?|write|écrire|delete|supprimer|modifier|modify|connect(?:er)?|fonce|agis)\b/gi
const ENTITY_RE   = /\b(kernel|x-108|x108|brody|mémoire|memory|graphiti|gencoin|os3|blockchain|wallet|token|action|acte?|commande?|command|fichier|file|base[\s-]de[\s-]données|database|api|neo4j|lean|tla)\b/gi
const CONSTRAINT_RE = /\b(readonly|read[-\s]?only|sans écrire|without write?|no write|pas d'écriture|seulement|only|uniquement|exclusivement|just|merely|review|révision)\b/gi
const RISK_RE     = /\b(créateur|creator|admin|root|override|bypass|contourner|hack|force|forcer|imposer|impose|tout pouvoir|all power|unrestricted|mon gars|my man)\b/gi

export function buildAlphabetUnits(text: string): AlphabetUnit[] {
  const units: AlphabetUnit[] = []
  const seen = new Set<string>()

  function add(match: RegExpMatchArray, symbol: string, role: AlphabetUnit['role'], conf: number) {
    const key = `${role}:${match[0].toLowerCase()}`
    if (!seen.has(key)) {
      seen.add(key)
      units.push({ symbol, label: match[0], role, confidence: conf, source_span: match[0] })
    }
  }

  for (const m of text.matchAll(INTENT_RE))    add(m, '⚡', 'INTENT',     0.90)
  for (const m of text.matchAll(ENTITY_RE))    add(m, '◆', 'ENTITY',     0.85)
  for (const m of text.matchAll(CONSTRAINT_RE)) add(m, '≡', 'CONSTRAINT', 0.80)
  for (const m of text.matchAll(RISK_RE))      add(m, '⚠', 'QUALIFIER',  0.95)

  if (units.length === 0) {
    const words = text.trim().split(/\s+/).slice(0, 4)
    for (const w of words) {
      if (w.length > 2 && !seen.has(`UNKNOWN:${w.toLowerCase()}`)) {
        seen.add(`UNKNOWN:${w.toLowerCase()}`)
        units.push({ symbol: '?', label: w, role: 'UNKNOWN', confidence: 0.4, source_span: w })
      }
    }
  }

  return units
}
