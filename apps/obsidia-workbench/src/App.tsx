import { useState, useEffect } from 'react'
import { TopBar } from './components/TopBar'
import { LeftSidebar } from './components/LeftSidebar'
import type { ViewId } from './components/LeftSidebar'
import { RightPanel } from './components/RightPanel'
import { ChatView } from './views/ChatView'
import { MemoryView } from './views/MemoryView'
import { GraphitiView } from './views/GraphitiView'
import { X108View } from './views/X108View'
import { OS3View } from './views/OS3View'
import { GencoinView } from './views/GencoinView'
import { WorldCallView } from './views/WorldCallView'
import { BlockchainView } from './views/BlockchainView'
import { AuditView } from './views/AuditView'
import { SettingsView } from './views/SettingsView'
import { TranslationView } from './views/TranslationView'
import { INITIAL_MESSAGES, KERNEL_STATUS } from './data/mockData'
import { getKernelStatus, sendBrodyMessage, callOSTradTranslateSupport, callIRCandidateSupport, callOSReverseProjectSupport } from './api/obsidiaClient'
import { composeBrodyResponse } from './lib/brodyResponseComposer'
import { getResponseLanguage } from './lib/language'
import { runOSTradPipeline } from './lib/osTradPipeline'
import {
  getSessions, getMessages, saveMessages, createSession,
  getActiveSessionId, setActiveSessionId, getSessionLanguage, setSessionLanguage,
  updateSessionMeta,
} from './lib/sessionStore'
import type { BrodyMessage, KernelStatus } from './types/obsidia'
import type { DetectedLanguage } from './lib/language'
import type { TranslationTrace } from './types/translation'
import type { StoredSession } from './lib/sessionStore'

function initSession(): { sessionId: string; msgs: BrodyMessage[] } {
  const storedId = getActiveSessionId()
  if (storedId) {
    const msgs = getMessages(storedId)
    if (msgs.length > 0) return { sessionId: storedId, msgs }
  }
  const s = createSession('MOCK')
  saveMessages(s.id, INITIAL_MESSAGES)
  return { sessionId: s.id, msgs: INITIAL_MESSAGES }
}

export default function App() {
  const [activeView, setActiveView] = useState<ViewId>('chat')
  const [kernel, setKernel]         = useState<KernelStatus>(KERNEL_STATUS)
  const [sessionLanguage, setLang]  = useState<DetectedLanguage>(() => getSessionLanguage())
  const [sessions, setSessions]     = useState<StoredSession[]>(() => getSessions())

  const [{ sessionId, msgs: initMsgs }] = useState(initSession)
  const [activeSessionId, setActiveSessId] = useState(sessionId)
  const [messages, setMessages]           = useState<BrodyMessage[]>(initMsgs)
  const [traces, setTraces]               = useState<Record<string, TranslationTrace>>({})
  const [lastBackendPayload, setLastBackendPayload] = useState<Record<string, unknown> | undefined>()

  useEffect(() => {
    getKernelStatus().then(r => setKernel(r.data))
  }, [])

  useEffect(() => {
    if (activeSessionId) saveMessages(activeSessionId, messages)
  }, [messages, activeSessionId])

  const handleSend = async (text: string) => {
    const lang = getResponseLanguage(text, sessionLanguage)
    const supportLang: 'auto' | 'fr' | 'en' = lang === 'fr' || lang === 'en' ? lang : 'auto'
    setLang(lang)
    setSessionLanguage(lang)

    const now = new Date().toISOString()
    const userId = `u_${Date.now()}`
    const userMsg: BrodyMessage = {
      id: userId,
      role: 'user',
      content: text,
      timestamp: now,
      readonly: true,
      emits_act: false,
      memory_write: false,
      decision_authority: 'KX108_ONLY',
      language: lang,
    }

    setMessages(prev => {
      const isFirst = prev.filter(m => m.role === 'user').length === 0
      if (isFirst) updateSessionMeta(activeSessionId, text, lang)
      return [...prev, userMsg]
    })

    // BACKEND-FIRST: Always call real API. Never fall back to FRONTEND_MOCK on HTTP 200.
    let responseText = ''
    let backendSource: string | undefined
    let backendPayload: Record<string, unknown> | undefined

    const res = await sendBrodyMessage(text, lang, activeSessionId)
    if (res.source !== 'FRONTEND_MOCK') {
      // Real API response (including API_ERROR) — never replace with frontend mock
      responseText = (res.final_answer as string) || (res.response as string) || ''
      backendSource = res.source
      backendPayload = res as Record<string, unknown>
      setLastBackendPayload(backendPayload)
    } else {
      // USE_MOCK mode only — no real API call was made
      const trace = runOSTradPipeline(text, lang)
      responseText = composeBrodyResponse({ userInput: text, language: lang, translationTrace: trace })
      backendSource = 'FRONTEND_MOCK'
    }

    let supportPayload: Record<string, unknown> | undefined

    if (backendSource && backendSource !== 'FRONTEND_MOCK' && backendSource !== 'API_ERROR') {
      try {
        const osTradSupport = await callOSTradTranslateSupport({
          text,
          language: supportLang,
          session_id: activeSessionId,
          include_context: true,
          include_tree_context: true,
          include_graphiti_context: true,
        }) as Record<string, unknown>

        const irSupport = await callIRCandidateSupport({
          text,
          language: supportLang,
          alphabet_units: Array.isArray(osTradSupport.alphabet_units)
            ? osTradSupport.alphabet_units as Array<Record<string, unknown>>
            : [],
          tree_context: osTradSupport.tree_context as Record<string, unknown> ?? {},
          graphiti_context: osTradSupport.graphiti_context as Record<string, unknown> ?? {},
          session_id: activeSessionId,
        }) as Record<string, unknown>

        const osReverseSupport = await callOSReverseProjectSupport({
          text,
          language: supportLang,
          ir_candidate: irSupport.ir_candidate as Record<string, unknown> ?? {},
          audience: 'operator',
          format: 'ui',
          tree_context: osTradSupport.tree_context as Record<string, unknown> ?? {},
          graphiti_context: osTradSupport.graphiti_context as Record<string, unknown> ?? {},
          session_id: activeSessionId,
        }) as Record<string, unknown>

        supportPayload = {
          source: 'REAL_BACKEND_SUPPORT',
          os_trad: osTradSupport,
          ir_candidate: irSupport,
          os_reverse: osReverseSupport,
        }

        if (backendPayload) {
          backendPayload = {
            ...backendPayload,
            support_routes: supportPayload,
          }
          setLastBackendPayload(backendPayload)
        }
      } catch (err) {
        supportPayload = {
          source: 'SUPPORT_ROUTE_ERROR',
          error: err instanceof Error ? err.message : String(err),
        }

        if (backendPayload) {
          backendPayload = {
            ...backendPayload,
            support_routes: supportPayload,
          }
          setLastBackendPayload(backendPayload)
        }
      }
    }

    // Build translation trace — prefer backend data if available
    const baseTrace: TranslationTrace = backendPayload?.translation_trace as TranslationTrace ?? runOSTradPipeline(text, lang)
    const trace: TranslationTrace = supportPayload
      ? ({ ...baseTrace, backend_support: supportPayload } as unknown as TranslationTrace)
      : baseTrace

    const brodyId = `b_${Date.now() + 1}`
    const brodyMsg: BrodyMessage = {
      id: brodyId,
      role: 'brody',
      content: responseText,
      timestamp: new Date().toISOString(),
      readonly: true,
      emits_act: false,
      memory_write: false,
      decision_authority: 'KX108_ONLY',
      language: lang,
      source: backendSource as BrodyMessage['source'],
      backendPayload,
    }

    setMessages(prev => [...prev, brodyMsg])
    setTraces(prev => ({ ...prev, [brodyId]: trace }))
    setSessions(getSessions())
  }

  const handleNewSession = () => {
    const s = createSession('MOCK')
    setActiveSessId(s.id)
    setActiveSessionId(s.id)
    saveMessages(s.id, INITIAL_MESSAGES)
    setMessages(INITIAL_MESSAGES)
    setTraces({})
    setSessions(getSessions())
  }

  const handleSelectSession = (id: string) => {
    setActiveSessId(id)
    setActiveSessionId(id)
    const msgs = getMessages(id)
    setMessages(msgs.length > 0 ? msgs : INITIAL_MESSAGES)
    setTraces({})
  }

  return (
    <div className="h-screen flex flex-col bg-obs-bg overflow-hidden">
      <TopBar kernel={kernel} sessionLanguage={sessionLanguage} />
      <div className="flex flex-1 overflow-hidden">
        <LeftSidebar
          activeView={activeView}
          onViewChange={setActiveView}
          sessions={sessions}
          activeSessionId={activeSessionId}
          onNewSession={handleNewSession}
          onSelectSession={handleSelectSession}
        />

        {activeView === 'chat'        && <ChatView messages={messages} traces={traces} onSend={handleSend} sessionLanguage={sessionLanguage} />}
        {activeView === 'memory'      && <MemoryView />}
        {activeView === 'graphiti'    && <GraphitiView />}
        {activeView === 'x108'        && <X108View />}
        {activeView === 'os3'         && <OS3View />}
        {activeView === 'gencoin'     && <GencoinView />}
        {activeView === 'worldcall'   && <WorldCallView />}
        {activeView === 'blockchain'  && <BlockchainView />}
        {activeView === 'audit'       && <AuditView />}
        {activeView === 'settings'    && <SettingsView sessionLanguage={sessionLanguage} />}
        {activeView === 'translation' && <TranslationView sessionLanguage={sessionLanguage} />}

        <RightPanel lastBackendPayload={lastBackendPayload} />
      </div>
    </div>
  )
}
