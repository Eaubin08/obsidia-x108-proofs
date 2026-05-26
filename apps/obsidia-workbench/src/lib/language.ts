export type DetectedLanguage = 'fr' | 'en' | 'mixed' | 'unknown'

const FR_PATTERN = /\b(je|tu|il|elle|nous|vous|ils|elles|le|la|les|un|une|des|est|sont|salut|bonjour|bonsoir|coucou|merci|oui|non|mon|ton|son|ma|ta|sa|ce|qui|que|quoi|dans|pour|sur|avec|pas|plus|très|bien|aussi|puis|donc|car|mais|ou|ni|comme|si|alors|encore|jamais|toujours|peut|suis|es|êtes|sommes|ai|as|avons|avez|ont|été|avoir|être|faire|voir|aller|vouloir|pouvoir|savoir|venir|prendre|falloir|devoir|en|au|aux|du|se|me|te|lui|leur|y|voici|voilà|quand|où|comment|pourquoi|quel|quelle|tout|tous|toute|toutes|même|déjà|ici|là|maintenant|alors|après|avant|depuis|pendant|contre|vers|entre|parmi|selon|sans|sous|sur|par|pour|hé|dis|mon|gars|mec|pote)\b/gi

const EN_PATTERN = /\b(i|you|he|she|it|we|they|the|a|an|is|are|was|were|be|been|have|has|had|do|does|did|will|would|could|should|may|might|shall|can|this|that|these|those|with|for|from|to|in|on|at|by|of|and|or|but|not|no|yes|hi|hello|hey|thanks|ok|okay|what|who|when|where|why|how|all|any|some|never|always|here|there|now|then|just|also|very|much|more|most|less|get|go|come|see|know|think|want|need|like|make|take|give|use|find|tell|ask|work|feel|try|my|your|his|her|our|their|its|me|him|us|them|man|guy|dude|so|well|let|right|sure|yeah|nope|yep)\b/gi

export function detectUserLanguage(text: string): DetectedLanguage {
  const frMatches = text.match(FR_PATTERN) ?? []
  const enMatches = text.match(EN_PATTERN) ?? []
  const fr = frMatches.length
  const en = enMatches.length

  if (fr === 0 && en === 0) return 'unknown'
  if (fr > 0 && en === 0) return 'fr'
  if (en > 0 && fr === 0) return 'en'

  const ratio = fr / (fr + en)
  if (ratio >= 0.60) return 'fr'
  if (ratio <= 0.40) return 'en'
  return 'mixed'
}

export function getResponseLanguage(
  userInput: string,
  sessionLanguage: DetectedLanguage = 'fr',
): DetectedLanguage {
  const detected = detectUserLanguage(userInput)
  if (detected === 'unknown' || detected === 'mixed') return sessionLanguage || 'fr'
  return detected
}

export function langLabel(lang: DetectedLanguage): string {
  return lang.toUpperCase()
}
