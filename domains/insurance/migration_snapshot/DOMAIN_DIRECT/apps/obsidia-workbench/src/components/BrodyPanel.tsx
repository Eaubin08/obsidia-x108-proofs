import { useState, useRef, useEffect } from 'react'
import { Send, Lock, AlertCircle } from 'lucide-react'
import type { BrodyMessage } from '../types/obsidia'

interface Props {
  messages: BrodyMessage[]
  onSend: (text: string) => void
}

function MessageBubble({ msg }: { msg: BrodyMessage }) {
  const isUser = msg.role === 'user'
  const ts = new Date(msg.timestamp).toLocaleTimeString()

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[72%]">
          <div className="bg-obs-border/80 text-obs-text rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm">
            {msg.content}
          </div>
          <div className="text-obs-dtext text-[10px] font-mono text-right mt-1 pr-1">{ts}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex gap-3 mb-4">
      <div className="w-7 h-7 rounded-full bg-obs-brody/20 border border-obs-brody/30 flex items-center justify-center shrink-0 mt-0.5">
        <span className="text-obs-brody text-[10px] font-mono font-bold">B</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-obs-brody text-xs font-mono font-semibold">Brody</span>
          <span className="obs-badge-brody">ADVISORY</span>
          <span className="obs-badge-muted">readonly=true</span>
          <span className="obs-badge-muted">emits_act=false</span>
        </div>
        <div className="bg-obs-card border border-obs-border rounded-2xl rounded-tl-sm px-4 py-3">
          <p className="text-obs-text text-sm leading-relaxed font-mono whitespace-pre-wrap">{msg.content}</p>
        </div>
        <div className="flex items-center gap-3 mt-1.5 pl-1">
          <span className="text-obs-dtext text-[10px] font-mono">{ts}</span>
          <span className="text-obs-dtext text-[10px] font-mono">decision_authority: <span className="text-obs-kernel">KX108_ONLY</span></span>
          <span className="text-obs-dtext text-[10px] font-mono">memory_write: <span className="text-obs-block">false</span></span>
        </div>
      </div>
    </div>
  )
}

export function BrodyPanel({ messages, onSend }: Props) {
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    const trimmed = input.trim()
    if (!trimmed) return
    onSend(trimmed)
    setInput('')
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-obs-bg">

      {/* Chat header */}
      <div className="h-10 bg-obs-surface border-b border-obs-border flex items-center px-4 gap-3 shrink-0">
        <span className="text-obs-brody font-mono text-xs font-semibold">Brody</span>
        <div className="h-3 w-px bg-obs-border" />
        <span className="obs-badge-brody">ADVISORY ONLY</span>
        <span className="obs-badge-muted">context_signal_only=true</span>
        <div className="ml-auto flex items-center gap-1.5">
          <Lock size={10} className="text-obs-dtext" />
          <span className="text-obs-dtext text-[10px] font-mono">no real action</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.map(m => <MessageBubble key={m.id} msg={m} />)}
        <div ref={bottomRef} />
      </div>

      {/* Disclaimer */}
      <div className="px-6 py-2 flex items-center gap-2 border-t border-obs-border/40">
        <AlertCircle size={10} className="text-obs-dtext shrink-0" />
        <span className="text-obs-dtext text-[10px] font-mono">
          Brody responses are advisory context signals only. No decision, no ACT, no memory write. X-108 kernel decides.
        </span>
      </div>

      {/* Input */}
      <div className="px-4 py-3 bg-obs-surface border-t border-obs-border">
        <div className="flex gap-2 items-end">
          <div className="flex-1 bg-obs-card border border-obs-border rounded-xl overflow-hidden focus-within:border-obs-brody/50 transition-colors">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              rows={2}
              placeholder="Query Brody (advisory response only)..."
              className="w-full bg-transparent text-obs-text text-sm font-mono px-4 py-2.5 resize-none outline-none placeholder:text-obs-dtext"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-obs-brody/20 border border-obs-brody/30 text-obs-brody text-xs font-mono font-semibold hover:bg-obs-brody/30 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={12} /> SUBMIT
          </button>
        </div>
      </div>
    </div>
  )
}
