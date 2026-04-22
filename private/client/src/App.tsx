import React, { useState, createContext, useContext } from "react";
import { Route, Switch, Link, useLocation, Redirect } from "wouter";
import { trpc } from "@/lib/trpc";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { httpBatchLink } from "@trpc/client";
import superjson from "superjson";
import { ViewModeProvider } from "@/contexts/ViewModeContext";
import { WorldProvider } from "@/contexts/WorldContext";
import ErrorBoundary from "@/components/ErrorBoundary";
import StatusRail from "@/components/StatusRail";

// ─── Pages V2 (5 surfaces temporelles) ───────────────────────────────────────
import Mission  from "@/pages/Mission";
import Live     from "@/pages/Live";
import Future   from "@/pages/Future";
import Past     from "@/pages/Past";
import Control  from "@/pages/Control";

// ─── Pages V1 (conservées pour pages orphelines accessibles directement) ─────
import OS4Home    from "@/pages/OS4Home";
import Simuler    from "@/pages/Simuler";
import Decision   from "@/pages/Decision";
import Preuves    from "@/pages/Preuves";
import Controle   from "@/pages/Controle";
import TradingWorld      from "@/pages/TradingWorld";
import BankWorld         from "@/pages/BankWorld";
import EcomWorld         from "@/pages/EcomWorld";
import DecisionFlow      from "@/pages/DecisionFlow";
import ProofCenter       from "@/pages/ProofCenter";
import ControlTower      from "@/pages/ControlTower";
import Portfolio         from "@/pages/Portfolio";
import DemoPage          from "@/pages/DemoPage";
import Agents            from "@/pages/Agents";
import Market            from "@/pages/Market";
import Predictions       from "@/pages/Predictions";
import HowItWorks        from "@/pages/HowItWorks";
import SimulationDashboard from "@/pages/SimulationDashboard";
import StressLab         from "@/pages/StressLab";
import AuditMode         from "@/pages/AuditMode";
import MirrorMode        from "@/pages/MirrorMode";
import DecisionReactor   from "@/pages/DecisionReactor";
import ScenarioEngine    from "@/pages/ScenarioEngine";
import GovernanceX108    from "@/pages/GovernanceX108";
import Roadmap           from "@/pages/Roadmap";
import DemoMode          from "@/pages/DemoMode";
import AutomatedTests    from "@/pages/AutomatedTests";
import DecisionLifecycle from "@/pages/DecisionLifecycle";
import SimulationWorlds  from "@/pages/SimulationWorlds";
import WhatIsObsidia     from "@/pages/WhatIsObsidia";
import ProofResearch     from "@/pages/ProofResearch";
import SourceVerification from "@/pages/SourceVerification";
import Evidence          from "@/pages/Evidence";
import UseCases          from "@/pages/UseCases";
import Technology        from "@/pages/Technology";
import Docs              from "@/pages/Docs";
import DecisionStreamPage from "@/pages/DecisionStream";

// ─── Portfolio Context ────────────────────────────────────────────────────────

export interface PortfolioState {
  capital: number;
  pnl24h: number;
  pnl24hPct: number;
  guardBlocks: number;
  capitalSaved: number;
  onTradingUpdate: (d: { pnl?: number; capital?: number }) => void;
  onBankUpdate: (d: { balance?: number }) => void;
  onGuardBlock: () => void;
}

export const PortfolioContext = createContext<PortfolioState>({
  capital: 125000,
  pnl24h: 0,
  pnl24hPct: 0,
  guardBlocks: 0,
  capitalSaved: 0,
  onTradingUpdate: () => {},
  onBankUpdate: () => {},
  onGuardBlock: () => {},
});

export const usePortfolio = () => useContext(PortfolioContext);

const queryClient = new QueryClient();
const trpcClient = trpc.createClient({
  links: [httpBatchLink({ url: "/api/trpc", transformer: superjson })],
});

// ─── Navigation V2 — 5 surfaces temporelles ──────────────────────────────────

const NAV_ITEMS = [
  { path: "/mission", label: "Mission", icone: "🎯" },
  { path: "/live",    label: "Live",    icone: "⚡" },
  { path: "/future",  label: "Future",  icone: "🔭" },
  { path: "/past",    label: "Past",    icone: "📚" },
  { path: "/control", label: "Control", icone: "🛡️" },
];

// ─── Header ───────────────────────────────────────────────────────────────────

function Header({ portfolio }: { portfolio: PortfolioState }) {
  const [location] = useLocation();
  const [menuMobile, setMenuMobile] = useState(false);

  const isActive = (path: string) =>
    path === "/mission"
      ? location === "/" || location === "/mission"
      : location === path || location.startsWith(path + "/");

  return (
    <header style={{ background: "oklch(0.10 0.01 240)", borderBottom: "1px solid oklch(0.20 0.01 240)" }}>
      {/* Barre principale */}
      <div className="flex items-center justify-between px-4 py-2" style={{ borderBottom: "1px solid oklch(0.16 0.01 240)" }}>
        {/* Logo */}
        <Link href="/mission">
          <span className="font-mono font-bold text-sm tracking-widest cursor-pointer" style={{ color: "oklch(0.72 0.18 145)" }}>
            OBSIDIA
          </span>
        </Link>

        {/* Pipeline indicateur — desktop */}
        <div className="hidden lg:flex items-center gap-1 text-[9px] font-mono">
          {["Observe", "Interpret", "Aggregate", "X-108", "Proof"].map((step, i) => (
            <React.Fragment key={step}>
              <span className="px-1.5 py-0.5 rounded" style={{
                background: "oklch(0.14 0.01 240)",
                color: step === "X-108" ? "oklch(0.72 0.18 145)" : step === "Proof" ? "#a78bfa" : "oklch(0.50 0.01 240)",
                border: step === "X-108" ? "1px solid oklch(0.72 0.18 145 / 0.4)" : "none",
              }}>{step}</span>
              {i < 4 && <span style={{ color: "oklch(0.30 0.01 240)" }}>→</span>}
            </React.Fragment>
          ))}
        </div>

        {/* Stats + CTA */}
        <div className="flex items-center gap-3 text-[10px] font-mono">
          <div className="hidden md:flex items-center gap-1.5">
            <span style={{ color: "oklch(0.45 0.01 240)" }}>Capital</span>
            <span className="font-bold text-foreground">{portfolio.capital.toLocaleString("fr-FR")} €</span>
          </div>
          <div className="hidden md:flex items-center gap-1.5">
            <span style={{ color: "oklch(0.45 0.01 240)" }}>Protégé</span>
            <span className="font-bold" style={{ color: "oklch(0.72 0.18 145)" }}>+{portfolio.capitalSaved.toLocaleString("fr-FR")} €</span>
          </div>
          <div className="flex items-center gap-1.5 px-2 py-1 rounded" style={{ background: "oklch(0.14 0.04 145)", border: "1px solid oklch(0.72 0.18 145 / 0.3)" }}>
            <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "oklch(0.72 0.18 145)" }} />
            <span style={{ color: "oklch(0.72 0.18 145)" }}>OS4</span>
          </div>
          {/* Bouton menu mobile */}
          <button
            className="md:hidden px-2 py-1 font-mono text-[10px]"
            style={{ color: "oklch(0.55 0.01 240)" }}
            onClick={() => setMenuMobile(v => !v)}
          >
            {menuMobile ? "✕" : "☰"}
          </button>
        </div>
      </div>

      {/* Navigation principale V2 — 5 surfaces */}
      <nav className={`flex items-center px-4 gap-1 ${menuMobile ? "flex-col items-start py-2" : "hidden md:flex"}`}>
        {NAV_ITEMS.map(item => (
          <Link
            key={item.path}
            href={item.path}
            onClick={() => setMenuMobile(false)}
            className="flex items-center gap-1.5 px-4 py-2.5 text-[11px] font-mono font-bold whitespace-nowrap transition-colors border-b-2"
            style={{
              color: isActive(item.path) ? "oklch(0.72 0.18 145)" : "oklch(0.55 0.01 240)",
              borderBottomColor: isActive(item.path) ? "oklch(0.72 0.18 145)" : "transparent",
              background: isActive(item.path) ? "oklch(0.13 0.02 145 / 0.3)" : "transparent",
              letterSpacing: "0.06em",
            }}
          >
            <span>{item.icone}</span>
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────

function AppContent() {
  const [ready, setReady] = React.useState(false);
  React.useEffect(() => { const t = setTimeout(() => setReady(true), 50); return () => clearTimeout(t); }, []);
  const [portfolio, setPortfolio] = useState<Omit<PortfolioState, "onTradingUpdate" | "onBankUpdate" | "onGuardBlock">>({
    capital: 125000,
    pnl24h: 1245,
    pnl24hPct: 1.0,
    guardBlocks: 0,
    capitalSaved: 0,
  });

  const portfolioCtx: PortfolioState = {
    ...portfolio,
    onTradingUpdate: (d) => setPortfolio((p) => ({ ...p, capital: d.capital ?? p.capital, pnl24h: d.pnl ?? p.pnl24h })),
    onBankUpdate: (d) => setPortfolio((p) => ({ ...p, capital: d.balance ?? p.capital })),
    onGuardBlock: () => setPortfolio((p) => ({ ...p, guardBlocks: p.guardBlocks + 1, capitalSaved: p.capitalSaved + 15000 })),
  };

  if (!ready) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: "oklch(0.09 0.01 240)" }}>
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{ borderColor: "oklch(0.72 0.18 145)", borderTopColor: "transparent" }} />
        <span className="font-mono text-[10px] tracking-widest" style={{ color: "oklch(0.45 0.01 240)" }}>OBSIDIA OS4 — Initialisation...</span>
      </div>
    </div>
  );

  return (
    <PortfolioContext.Provider value={portfolioCtx}>
      <div className="min-h-screen flex flex-col" style={{ background: "oklch(0.09 0.01 240)", color: "oklch(0.90 0.01 240)" }}>
        <Header portfolio={portfolioCtx} />
        <StatusRail />
        <main className="flex-1 overflow-auto">
          <Switch>
            {/* ─── V2 : 5 surfaces temporelles ─────────────────────────── */}
            <Route path="/mission"><ErrorBoundary><Mission /></ErrorBoundary></Route>
            <Route path="/live"><ErrorBoundary><Live /></ErrorBoundary></Route>
            <Route path="/future"><ErrorBoundary><Future /></ErrorBoundary></Route>
            <Route path="/past"><ErrorBoundary><Past /></ErrorBoundary></Route>
            <Route path="/control"><ErrorBoundary><Control /></ErrorBoundary></Route>

            {/* ─── Redirects V1 → V2 ────────────────────────────────────── */}
            <Route path="/"><Redirect to="/mission" /></Route>
            <Route path="/simuler"><Redirect to="/future" /></Route>
            <Route path="/decision"><Redirect to="/live" /></Route>
            <Route path="/preuves"><Redirect to="/past" /></Route>
            <Route path="/controle"><Redirect to="/control" /></Route>

            {/* ─── Démo ─────────────────────────────────────────────────── */}
            <Route path="/demo" component={DemoPage} />

            {/* ─── Redirections legacy ──────────────────────────────────── */}
            <Route path="/market"><Redirect to="/future" /></Route>
            <Route path="/market/trading"><Redirect to="/future" /></Route>
            <Route path="/market/banking"><Redirect to="/future" /></Route>
            <Route path="/market/ecommerce"><Redirect to="/future" /></Route>
            <Route path="/use-cases"><Redirect to="/mission" /></Route>
            <Route path="/use-cases/trading"><Redirect to="/future" /></Route>
            <Route path="/use-cases/banking"><Redirect to="/future" /></Route>
            <Route path="/use-cases/ecommerce"><Redirect to="/future" /></Route>
            <Route path="/simulation-worlds"><Redirect to="/future" /></Route>
            <Route path="/trading"             component={TradingWorld} />
            <Route path="/bank"                component={BankWorld} />
            <Route path="/ecom"               component={EcomWorld} />
            <Route path="/decision-flow"><Redirect to="/live" /></Route>
            <Route path="/decisions"><Redirect to="/live" /></Route>
            <Route path="/stream"><Redirect to="/live" /></Route>
            <Route path="/proof-center"><Redirect to="/past" /></Route>
            <Route path="/proof"><Redirect to="/past" /></Route>
            <Route path="/formal-proof"><Redirect to="/past" /></Route>
            <Route path="/evidence"><Redirect to="/past" /></Route>
            <Route path="/source"><Redirect to="/past" /></Route>
            <Route path="/portfolio"><Redirect to="/control" /></Route>
            <Route path="/agents"><Redirect to="/control" /></Route>
            <Route path="/predictions"><Redirect to="/control" /></Route>

            {/* ─── Pages orphelines (hors nav, accessibles directement) ─── */}
            <Route path="/engine"             component={SimulationDashboard} />
            <Route path="/stress"             component={StressLab} />
            <Route path="/audit"              component={AuditMode} />
            <Route path="/mirror"             component={MirrorMode} />
            <Route path="/reactor"            component={DecisionReactor} />
            <Route path="/scenario-engine"    component={ScenarioEngine} />
            <Route path="/governance"         component={GovernanceX108} />
            <Route path="/demo-mode"          component={DemoMode} />
            <Route path="/roadmap"            component={Roadmap} />
            <Route path="/decision-lifecycle" component={DecisionLifecycle} />
            <Route path="/automated-tests"    component={AutomatedTests} />
            <Route path="/how-it-works"       component={HowItWorks} />
            <Route path="/technology"         component={Technology} />
            <Route path="/docs"               component={Docs} />
            <Route path="/what-is-obsidia"    component={WhatIsObsidia} />

            {/* ─── 404 ──────────────────────────────────────────────────── */}
            <Route>
              <div className="flex flex-col items-center justify-center h-64 gap-4">
                <div className="text-2xl font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>404</div>
                <p className="text-sm font-mono" style={{ color: "oklch(0.40 0.01 240)" }}>Page introuvable</p>
                <Link href="/mission">
                  <span className="text-sm font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>← Retour à Mission</span>
                </Link>
              </div>
            </Route>
          </Switch>
        </main>

        {/* Footer */}
        <footer style={{ background: "oklch(0.085 0.01 240)", borderTop: "1px solid oklch(0.16 0.01 240)" }}>
          <div className="flex flex-wrap items-center justify-between px-6 py-3 gap-4">
            <div className="flex items-center gap-2">
              <span className="font-mono text-[9px] font-bold tracking-widest" style={{ color: "oklch(0.72 0.18 145)" }}>OBSIDIA</span>
              <span className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>OS4 — Gouvernance pour agents autonomes</span>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <span className="font-mono text-[9px]" style={{ color: "oklch(0.40 0.01 240)" }}>Code source :</span>
              {[
                { label: "Repository",     url: "https://github.com/Eaubin08/Obsidia-lab-trad" },
                { label: "Preuves Lean 4", url: "https://github.com/Eaubin08/Obsidia-lab-trad/tree/main/lean" },
                { label: "Documentation",  url: "https://github.com/Eaubin08/Obsidia-lab-trad/tree/main/docs" },
              ].map(link => (
                <a key={link.label} href={link.url} target="_blank" rel="noopener noreferrer"
                  className="font-mono text-[9px] transition-colors"
                  style={{ color: "oklch(0.50 0.01 240)" }}
                  onMouseOver={e => (e.currentTarget.style.color = "oklch(0.72 0.18 145)")}
                  onMouseOut={e => (e.currentTarget.style.color = "oklch(0.50 0.01 240)")}>
                  {link.label} ↗
                </a>
              ))}
            </div>
          </div>
        </footer>
      </div>
    </PortfolioContext.Provider>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <trpc.Provider client={trpcClient} queryClient={queryClient}>
        <ViewModeProvider>
          <WorldProvider>
            <AppContent />
          </WorldProvider>
        </ViewModeProvider>
      </trpc.Provider>
    </QueryClientProvider>
  );
}
