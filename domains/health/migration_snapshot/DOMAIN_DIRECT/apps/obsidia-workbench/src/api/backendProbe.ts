export type ModuleStatus = 'LIVE' | 'MOCK' | 'STUB' | 'OFFLINE' | 'ERROR'

export interface ModuleProbe {
  name: string
  status: ModuleStatus
  endpoint: string
  port: number
  lastChecked: string
  latencyMs?: number
}

const API_BASE    = (import.meta.env.VITE_OBSIDIA_API_BASE ?? 'http://127.0.0.1:8011').replace(/\/$/, '')
const ENGINE_BASE = (import.meta.env.VITE_ENGINE_API_BASE  ?? 'http://127.0.0.1:8012').replace(/\/$/, '')
const USE_MOCK    = import.meta.env.VITE_USE_MOCK_FALLBACK === 'true'
const TIMEOUT_MS  = Number(import.meta.env.VITE_PROBE_TIMEOUT_MS ?? 2500)

const MODULES = [
  { name: 'ObsidiaShell',      endpoint: `${API_BASE}/health`,                     port: 8011, stub: false },
  { name: 'Graphiti V20',      endpoint: `${API_BASE}/graph/v20/frozen/status`,    port: 8011, stub: false },
  { name: 'X108 Engine',       endpoint: `${ENGINE_BASE}/api/x108/status`,         port: 8000, stub: true  },
  { name: 'Brody Runtime',     endpoint: `${ENGINE_BASE}/api/brody/chat`,          port: 8000, stub: true  },
  { name: 'ContextPacket API', endpoint: `${ENGINE_BASE}/api/context`,             port: 8000, stub: true  },
  { name: 'OS3 API',           endpoint: `${ENGINE_BASE}/api/os3`,                 port: 8000, stub: true  },
  { name: 'Gencoin API',       endpoint: `${ENGINE_BASE}/api/gencoin`,             port: 8000, stub: true  },
  { name: 'WorldCall API',     endpoint: `${ENGINE_BASE}/api/worldcalls`,          port: 8000, stub: true  },
  { name: 'Blockchain Gate',   endpoint: `${ENGINE_BASE}/api/blockchain/status`,   port: 8000, stub: true  },
  { name: 'Memory Ledger',     endpoint: `${ENGINE_BASE}/api/memory`,              port: 8000, stub: true  },
  { name: 'OS Trad',           endpoint: `${ENGINE_BASE}/api/os-trad/translate`,   port: 8000, stub: true  },
  { name: 'IR Candidate',      endpoint: `${ENGINE_BASE}/api/ir/candidate`,        port: 8000, stub: true  },
  { name: 'OS Reverse',        endpoint: `${ENGINE_BASE}/api/os-reverse/project`,  port: 8000, stub: true  },
]

async function probeOne(url: string): Promise<{ ok: boolean; latencyMs: number }> {
  const t0 = Date.now()
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(TIMEOUT_MS) })
    return { ok: res.ok, latencyMs: Date.now() - t0 }
  } catch {
    return { ok: false, latencyMs: Date.now() - t0 }
  }
}

export async function probeAllModules(): Promise<ModuleProbe[]> {
  const now = new Date().toLocaleTimeString()

  if (USE_MOCK) {
    return MODULES.map(m => ({
      name: m.name,
      status: 'MOCK' as ModuleStatus,
      endpoint: m.endpoint,
      port: m.port,
      lastChecked: now,
    }))
  }

  return Promise.all(
    MODULES.map(async m => {
      if (m.stub) {
        return { name: m.name, status: 'STUB' as ModuleStatus, endpoint: m.endpoint, port: m.port, lastChecked: now }
      }
      const { ok, latencyMs } = await probeOne(m.endpoint)
      return {
        name: m.name,
        status: (ok ? 'LIVE' : 'OFFLINE') as ModuleStatus,
        endpoint: m.endpoint,
        port: m.port,
        lastChecked: now,
        latencyMs,
      }
    }),
  )
}
