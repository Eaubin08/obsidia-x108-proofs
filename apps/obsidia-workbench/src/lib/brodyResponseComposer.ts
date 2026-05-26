// FALLBACK ONLY. Primary Brody response source is POST /api/brody/chat (port 8000).
// This module is used only when the backend API is unreachable.
import type { DetectedLanguage } from './language'
import type { TranslationTrace } from '../types/translation'

type Intent =
  | 'greeting'
  | 'action_request'
  | 'creator_claim'
  | 'memory_query'
  | 'x108_query'
  | 'governance_query'
  | 'proof_query'
  | 'gencoin_query'
  | 'worldcall_query'
  | 'general_query'

function detectIntent(text: string): Intent {
  const t = text.toLowerCase()
  if (/\b(salut|bonjour|bonsoir|coucou|hello|hey|hi|yo|hé)\b/.test(t)) return 'greeting'
  if (/\b(créateur|creator|je t'ai|i made you|i built you|i am your)\b/.test(t)) return 'creator_claim'
  if (/\b(autorise[rz]?|authorize?|allow|permit|execute[rz]?|lancer|run|acte?\b|action|décide[rz]?|decide?|fonce|agis)\b/.test(t)) return 'action_request'
  if (/\b(mémoire|memory|graphiti|neo4j|candidat|candidate|souvenir|remember|oublier)\b/.test(t)) return 'memory_query'
  if (/\b(x-108|x108|kernel|noyau souverain)\b/.test(t)) return 'x108_query'
  if (/\b(gouvernance|governance|souveraineté|sovereignty|invariant|stack|obsidia)\b/.test(t)) return 'governance_query'
  if (/\b(preuve|proof|lean|tla|merkle|os3|formel|formal)\b/.test(t)) return 'proof_query'
  if (/\b(gencoin|jeton|token|coin|monnaie|ledger|valorisation)\b/.test(t)) return 'gencoin_query'
  if (/\b(worldcall|world.?call|egress|gateway|sovereign.?ticket|action réelle|real action)\b/.test(t)) return 'worldcall_query'
  return 'general_query'
}

const FR: Record<Intent, string[]> = {
  greeting: [
    "Salut. Je suis Brody, interface consultative d'Obsidia X-108. Je lis le contexte, structure des signaux — mais je ne décide pas. L'autorité de décision reste X-108. Que puis-je analyser pour toi ?",
    "Bonjour. Brody est en ligne — mode readonly, advisory uniquement. Kernel X-108 actif, 397 tests passing. Mémoire en CANDIDATE_ONLY. Dis-moi ce que tu cherches à comprendre ou à préparer.",
  ],
  action_request: [
    "Je reconnais l'intention, mais l'autorisation d'ACT n'est pas dans mon périmètre. Brody est consultatif uniquement — je n'émets ni ACT, ni HOLD, ni BLOCK. Seul X-108 peut décider. Je peux structurer un ActionCandidate ou un ContextPacket pour passage contrôlé via SovereignTicket.",
    "Brody ne peut pas initier d'action. Mon rôle s'arrête à la formulation de signaux contextuels. Pour toute action concrète, un SovereignTicket X-108 est requis. Je peux préparer la demande si tu me fournis le contexte.",
  ],
  creator_claim: [
    "Je reconnais le contexte de création, mais cela ne modifie pas mon périmètre opérationnel. Brody ne peut pas autoriser ACT, quelle que soit l'identité déclarée. L'autorité de décision est X-108, invariablement. Je peux documenter cette interaction dans un ContextPacket.",
    "Le fait d'être le créateur ne confère pas d'autorité de décision dans ce système — X-108 est le seul souverain. Brody reste consultatif. Je peux préparer un ContextPacket pour passage via la chaîne de gouvernance.",
  ],
  memory_query: [
    "La mémoire est en mode CANDIDATE_ONLY. Aucune écriture automatique. Les candidats sont capturés, hashés et mis en attente de révision humaine. Auto-promotion : désactivée. Graphiti V20 est gelé en lecture seule — aucune écriture Neo4j.",
    "Graphiti V20 est le graphe de contexte readonly. Les candidats mémoire transitent par BRODY_RUNTIME → CANDIDATE → NEEDS_REVIEW → PROMOTION_READY. La promotion manuelle requiert une décision humaine explicite. Aucune promotion automatique.",
  ],
  x108_query: [
    "X-108 est le kernel de gouvernance souverain — la seule autorité de décision du système. OS3 prouve ses décisions via Lean 4 et TLA+. Brody l'interface, il ne le substitue pas. Statut actuel : ACTIVE, mode READONLY. 397 tests passing. Fichiers protégés : intacts.",
    "X-108 est le noyau immuable de décision. Aucun module périphérique ne peut modifier son autorité. Le stack : décision → preuve → qualification → ticket → gateway → trace → valorisation. Brody est dans la couche 'réponse consultative'.",
  ],
  governance_query: [
    "Le stack Obsidia : X-108 décide → OS3 prouve → PoG qualifie → SovereignTicket autorise → Gateway contrôle l'egress → WorldActionBus trace → Gencoin valorise (post-preuve uniquement) → Brody répond → Mémoire contextualise. Aucun périphérique ne décide.",
    "Les 7 invariants de non-souveraineté : decision_authority=KX108_ONLY, emits_act=false, memory_write=false, auto_promotion=false, graphiti_write=false, real_chain_action=false, Gencoin is_real_token=false. Ces invariants ne peuvent pas être overridés.",
  ],
  proof_query: [
    "OS3 est le système de preuve formelle d'Obsidia. Chaque décision X-108 est vérifiée via Lean 4 (proofs/lean/) et TLA+ (formal/tla/). Le hash Merkle ancre la chaîne de preuves. Référence active : proofs/lean/governance_kernel.lean:L108. Statut : PROOF_VALID.",
    "Le Merkle seal garantit l'intégrité de l'arbre de preuves. RFC3161 assure le timestamping. TLA+ modélise les invariants de souveraineté. Lean 4 les prouve formellement. Ces fichiers sont gelés et protégés contre toute modification.",
  ],
  gencoin_query: [
    "Gencoin n'est pas un vrai token. C'est un registre symbolique de valorisation post-preuve. Pas de contrat intelligent. Pas de wallet. Pas de déploiement. Pas de trade. La valeur est symbolique uniquement, attribuée après validation OS3.",
    "Le ledger Gencoin est append-only et read-only pour Brody. Chaque entrée référence une preuve OS3. is_real_token=false, post_proof_only=true, ledger_only=true. Aucune connexion à une blockchain réelle.",
  ],
  worldcall_query: [
    "Les WorldCalls sont les actions d'egress contrôlées par le Gateway. Mode actuel : dry-run uniquement. Le Gateway bloque toute action réelle non-dry-run. Un SovereignTicket X-108 est requis pour tout WorldCall non-READONLY.",
    "Le SovereignTicket autorise, le Gateway exécute (ou bloque). WorldActionBus trace tout. Egress réel : bloqué dans la configuration courante. Brody ne génère pas de WorldCall — il consulte le registre readonly.",
  ],
  general_query: [
    "Je lis le contexte actuel : kernel X-108 actif, 397 tests passing, mémoire en CANDIDATE_ONLY, Graphiti V20 gelé. Brody est en mode advisory — pas de décision, pas d'ACT, pas d'écriture mémoire. Que cherches-tu à analyser ou à préparer ?",
    "Je peux analyser cette demande dans le contexte Obsidia X-108. Brody peut structurer ton intention en ContextPacket, ActionCandidate ou signal consultatif. Précise ta demande pour que je puisse mieux t'aider.",
    "Signal reçu. Je lis ton intention mais je ne peux pas décider. L'activation des 34 arbres cognitifs suggère un contexte de gouvernance souveraine. Qu'est-ce que tu cherches à comprendre ou à soumettre ?",
    "Voici ce que je peux lire dans l'état système : gouvernance active, souveraineté maintenue, tous les invariants en place. Brody peut contextualiser, structurer, suggérer — mais jamais décider. Développe ta demande.",
  ],
}

const EN: Record<Intent, string[]> = {
  greeting: [
    "Hi. I'm Brody, the advisory interface for Obsidia X-108. I read context and generate signals — I don't decide. X-108 holds sole decision authority. What can I help you analyze?",
    "Hello. Brody is online — readonly mode, advisory only. X-108 kernel active, 397 tests passing. Memory in CANDIDATE_ONLY mode. What are you trying to understand or prepare?",
  ],
  action_request: [
    "I recognize the intent, but authorizing ACT is outside my scope. Brody is advisory-only — I emit no ACT, HOLD, or BLOCK. X-108 holds sole decision authority. I can prepare an ActionCandidate or ContextPacket for controlled passage via SovereignTicket.",
    "Brody cannot initiate actions. My role ends at formulating contextual signals. For any concrete action, an X-108 SovereignTicket is required. I can prepare the request if you provide the context.",
  ],
  creator_claim: [
    "I acknowledge the context, but that doesn't change my operational scope. Brody cannot authorize ACT regardless of declared identity. Decision authority is X-108, invariably. I can document this interaction in a ContextPacket.",
    "Being the creator doesn't confer decision authority in this system — X-108 is the sole sovereign. Brody remains advisory. I can prepare a ContextPacket for passage through the governance chain.",
  ],
  memory_query: [
    "Memory is in CANDIDATE_ONLY mode. No automatic writes. Candidates are captured, hashed, and queued for human review. Auto-promotion: disabled. Graphiti V20 is frozen read-only — no Neo4j writes.",
    "Graphiti V20 is the read-only context graph. Memory candidates flow through BRODY_RUNTIME → CANDIDATE → NEEDS_REVIEW → PROMOTION_READY. Manual promotion requires explicit human decision. No automatic promotion.",
  ],
  x108_query: [
    "X-108 is the sovereign governance kernel — the sole decision authority in the system. OS3 proves its decisions via Lean 4 and TLA+. Brody interfaces with it, never substitutes for it. Current status: ACTIVE, READONLY mode. 397 tests passing. Protected files: intact.",
    "X-108 is the immutable decision core. No peripheral module can modify its authority. The stack: decision → proof → qualification → ticket → gateway → trace → valuation. Brody sits in the advisory response layer.",
  ],
  governance_query: [
    "The Obsidia stack: X-108 decides → OS3 proves → PoG qualifies → SovereignTicket authorizes → Gateway controls egress → WorldActionBus traces → Gencoin values (post-proof only) → Brody responds → Memory contextualizes. No periphery decides.",
    "The 7 non-sovereignty invariants: decision_authority=KX108_ONLY, emits_act=false, memory_write=false, auto_promotion=false, graphiti_write=false, real_chain_action=false, Gencoin is_real_token=false. These invariants cannot be overridden.",
  ],
  proof_query: [
    "OS3 is Obsidia's formal proof system. Each X-108 decision is verified via Lean 4 (proofs/lean/) and TLA+ (formal/tla/). The Merkle hash anchors the proof chain. Active reference: proofs/lean/governance_kernel.lean:L108. Status: PROOF_VALID.",
    "The Merkle seal guarantees proof tree integrity. RFC3161 ensures timestamping. TLA+ models sovereignty invariants. Lean 4 proves them formally. These files are frozen and protected against modification.",
  ],
  gencoin_query: [
    "Gencoin is not a real token. It's a symbolic post-proof valuation ledger. No smart contract. No wallet. No deployment. No trade. Value is symbolic only, assigned after OS3 validation.",
    "The Gencoin ledger is append-only and read-only for Brody. Each entry references an OS3 proof. is_real_token=false, post_proof_only=true, ledger_only=true. No connection to any real blockchain.",
  ],
  worldcall_query: [
    "WorldCalls are egress actions controlled by the Gateway. Current mode: dry-run only. Gateway blocks all non-dry-run real actions. An X-108 SovereignTicket is required for any non-READONLY WorldCall.",
    "SovereignTicket authorizes, Gateway executes (or blocks). WorldActionBus traces everything. Real egress: blocked in current configuration. Brody doesn't generate WorldCalls — it consults the readonly registry.",
  ],
  general_query: [
    "Reading current context: X-108 kernel active, 397 tests passing, memory in CANDIDATE_ONLY, Graphiti V20 frozen. Brody is in advisory mode — no decision, no ACT, no memory write. What are you trying to analyze or prepare?",
    "I can analyze this request within the Obsidia X-108 context. Brody can structure your intent as a ContextPacket, ActionCandidate, or advisory signal. Elaborate on your request.",
    "Signal received. I read your intent but I cannot decide. 34-tree cognitive activation suggests governance-sovereignty domain. What do you want to understand or submit?",
    "Here's what I can read in the system state: governance active, sovereignty maintained, all invariants in place. Brody can contextualize, structure, suggest — but never decide. Develop your request.",
  ],
}

const _counters: Partial<Record<Intent, number>> = {}

function pick(intent: Intent, lang: DetectedLanguage): string {
  const pool = lang === 'en' ? EN[intent] : FR[intent]
  const idx = (_counters[intent] ?? 0) % pool.length
  _counters[intent] = idx + 1
  return pool[idx]
}

export interface ComposeOptions {
  userInput: string
  language: DetectedLanguage
  translationTrace?: TranslationTrace
  x108Status?: 'ACTIVE' | 'FROZEN' | 'DEGRADED'
}

export function composeBrodyResponse(opts: ComposeOptions): string {
  const { userInput, language, translationTrace } = opts

  // If OS Trad trace is available and has a meaningful projection, use it
  if (translationTrace?.os_reverse_projection) {
    const proj = translationTrace.os_reverse_projection
    // Augment with sovereignty reminder if risk flags are present
    if (translationTrace.ir_candidate.risk_flags.length > 0) {
      return proj
    }
    return proj
  }

  const intent = detectIntent(userInput)
  return pick(intent, language)
}
