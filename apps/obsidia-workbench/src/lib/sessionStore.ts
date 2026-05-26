import type { BrodyMessage } from '../types/obsidia'
import type { DetectedLanguage } from './language'

export interface StoredSession {
  id: string
  preview: string
  language: DetectedLanguage
  createdAt: string
  lastMessageAt: string
  backendMode: 'MOCK' | 'LIVE'
}

const SESSIONS_KEY = 'obs_sessions'
const MESSAGES_PREFIX = 'obs_msgs_'
const ACTIVE_KEY = 'obs_active'
const LANG_KEY = 'obs_lang'

function randId(): string {
  return `sess_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 5)}`
}

export function getSessions(): StoredSession[] {
  try { return JSON.parse(localStorage.getItem(SESSIONS_KEY) ?? '[]') }
  catch { return [] }
}

function saveSessions(ss: StoredSession[]): void {
  localStorage.setItem(SESSIONS_KEY, JSON.stringify(ss.slice(0, 20)))
}

export function getMessages(sessionId: string): BrodyMessage[] {
  try { return JSON.parse(localStorage.getItem(MESSAGES_PREFIX + sessionId) ?? '[]') }
  catch { return [] }
}

export function saveMessages(sessionId: string, msgs: BrodyMessage[]): void {
  localStorage.setItem(MESSAGES_PREFIX + sessionId, JSON.stringify(msgs))
}

export function getActiveSessionId(): string | null {
  return localStorage.getItem(ACTIVE_KEY)
}

export function setActiveSessionId(id: string): void {
  localStorage.setItem(ACTIVE_KEY, id)
}

export function getSessionLanguage(): DetectedLanguage {
  return (localStorage.getItem(LANG_KEY) as DetectedLanguage) ?? 'fr'
}

export function setSessionLanguage(lang: DetectedLanguage): void {
  localStorage.setItem(LANG_KEY, lang)
}

export function createSession(backendMode: 'MOCK' | 'LIVE' = 'MOCK'): StoredSession {
  const s: StoredSession = {
    id: randId(),
    preview: 'Nouvelle session',
    language: 'fr',
    createdAt: new Date().toISOString(),
    lastMessageAt: new Date().toISOString(),
    backendMode,
  }
  const sessions = getSessions()
  sessions.unshift(s)
  saveSessions(sessions)
  setActiveSessionId(s.id)
  return s
}

export function updateSessionMeta(
  sessionId: string,
  preview: string,
  language: DetectedLanguage,
): void {
  const sessions = getSessions()
  const idx = sessions.findIndex(s => s.id === sessionId)
  if (idx >= 0) {
    sessions[idx].preview = preview.slice(0, 45)
    sessions[idx].language = language
    sessions[idx].lastMessageAt = new Date().toISOString()
    saveSessions(sessions)
  }
}

export function deleteSession(sessionId: string): void {
  const sessions = getSessions().filter(s => s.id !== sessionId)
  saveSessions(sessions)
  localStorage.removeItem(MESSAGES_PREFIX + sessionId)
}

export function formatSessionLabel(s: StoredSession): string {
  const t = new Date(s.lastMessageAt).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
  return `${s.language.toUpperCase()} · ${s.preview} · ${t}`
}
