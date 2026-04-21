import { useAuth } from "@/_core/hooks/useAuth";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
import { getLoginUrl } from "@/const";
import { useIsMobile } from "@/hooks/useMobile";
import {
  Activity,
  BarChart3,
  ChevronDown,
  Clock,
  Cpu,
  FlaskConical,
  Globe,
  LayoutDashboard,
  LogOut,
  Monitor,
  PanelLeft,
  Shield,
  Telescope,
  TrendingUp,
  Zap,
} from "lucide-react";
import { CSSProperties, useEffect, useRef, useState } from "react";
import { useLocation } from "wouter";
import { DashboardLayoutSkeleton } from './DashboardLayoutSkeleton';
import { Button } from "./ui/button";

// ─── Navigation V2 ────────────────────────────────────────────────────────────
const MAIN_NAV = [
  { icon: LayoutDashboard, label: "Mission",  path: "/mission",  desc: "Point d'entrée" },
  { icon: Activity,        label: "Live",     path: "/live",     desc: "Console du présent" },
  { icon: Telescope,       label: "Future",   path: "/future",   desc: "Cockpit de simulation" },
  { icon: Clock,           label: "Past",     path: "/past",     desc: "Registre prouvé" },
  { icon: Shield,          label: "Control",  path: "/control",  desc: "Tour de commandement" },
];

const WORLD_NAV = [
  { icon: TrendingUp, label: "Trading",  path: "/trading",  color: "oklch(0.72 0.18 145)" },
  { icon: BarChart3,  label: "Bank",     path: "/bank",     color: "oklch(0.65 0.15 220)" },
  { icon: Globe,      label: "Ecom",     path: "/ecom",     color: "oklch(0.70 0.15 30)"  },
];

const TOOL_NAV = [
  { icon: Zap,         label: "Stress Lab",  path: "/stress"  },
  { icon: Monitor,     label: "Mirror Mode", path: "/mirror"  },
  { icon: Cpu,         label: "Engine",      path: "/engine"  },
  { icon: FlaskConical,label: "Scenarios",   path: "/scenario-engine" },
];

const SIDEBAR_WIDTH_KEY = "sidebar-width";
const DEFAULT_WIDTH = 240;
const MIN_WIDTH = 180;
const MAX_WIDTH = 380;

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarWidth, setSidebarWidth] = useState(() => {
    const saved = localStorage.getItem(SIDEBAR_WIDTH_KEY);
    return saved ? parseInt(saved, 10) : DEFAULT_WIDTH;
  });
  const { loading, user } = useAuth();

  useEffect(() => {
    localStorage.setItem(SIDEBAR_WIDTH_KEY, sidebarWidth.toString());
  }, [sidebarWidth]);

  if (loading) {
    return <DashboardLayoutSkeleton />;
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen" style={{ background: "oklch(0.08 0.01 240)" }}>
        <div className="flex flex-col items-center gap-8 p-8 max-w-md w-full">
          <div className="flex flex-col items-center gap-3">
            <div className="text-xs font-mono tracking-widest uppercase mb-2" style={{ color: "oklch(0.72 0.18 145)" }}>OS4 — OBSIDIA</div>
            <h1 className="text-xl font-semibold tracking-tight text-center" style={{ color: "oklch(0.92 0.01 240)" }}>
              Accès restreint
            </h1>
            <p className="text-sm text-center max-w-sm" style={{ color: "oklch(0.55 0.01 240)" }}>
              La plateforme de gouvernance X-108 requiert une authentification.
            </p>
          </div>
          <Button
            onClick={() => { window.location.href = getLoginUrl(); }}
            size="lg"
            className="w-full"
            style={{ background: "oklch(0.72 0.18 145)", color: "oklch(0.08 0.01 240)" }}
          >
            Se connecter
          </Button>
        </div>
      </div>
    );
  }

  return (
    <SidebarProvider
      style={{ "--sidebar-width": `${sidebarWidth}px` } as CSSProperties}
    >
      <DashboardLayoutContent setSidebarWidth={setSidebarWidth}>
        {children}
      </DashboardLayoutContent>
    </SidebarProvider>
  );
}

type DashboardLayoutContentProps = {
  children: React.ReactNode;
  setSidebarWidth: (width: number) => void;
};

function DashboardLayoutContent({ children, setSidebarWidth }: DashboardLayoutContentProps) {
  const { user, logout } = useAuth();
  const [location, setLocation] = useLocation();
  const { state, toggleSidebar } = useSidebar();
  const isCollapsed = state === "collapsed";
  const [isResizing, setIsResizing] = useState(false);
  const [toolsOpen, setToolsOpen] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);
  const isMobile = useIsMobile();
  const activeMain = MAIN_NAV.find(i => i.path === location);

  useEffect(() => {
    if (isCollapsed) setIsResizing(false);
  }, [isCollapsed]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      const sidebarLeft = sidebarRef.current?.getBoundingClientRect().left ?? 0;
      const newWidth = e.clientX - sidebarLeft;
      if (newWidth >= MIN_WIDTH && newWidth <= MAX_WIDTH) setSidebarWidth(newWidth);
    };
    const handleMouseUp = () => setIsResizing(false);
    if (isResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    }
    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isResizing, setSidebarWidth]);

  return (
    <>
      <div className="relative" ref={sidebarRef}>
        <Sidebar
          collapsible="icon"
          className="border-r-0"
          disableTransition={isResizing}
          style={{ background: "oklch(0.09 0.01 240)", borderRight: "1px solid oklch(0.15 0.01 240)" }}
        >
          {/* Header */}
          <SidebarHeader className="h-14 justify-center" style={{ borderBottom: "1px solid oklch(0.14 0.01 240)" }}>
            <div className="flex items-center gap-2 px-2">
              <button
                onClick={toggleSidebar}
                className="h-8 w-8 flex items-center justify-center rounded-lg transition-colors focus:outline-none"
                style={{ color: "oklch(0.55 0.01 240)" }}
                aria-label="Toggle navigation"
              >
                <PanelLeft className="h-4 w-4" />
              </button>
              {!isCollapsed && (
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-xs font-mono tracking-widest uppercase" style={{ color: "oklch(0.72 0.18 145)" }}>OS4</span>
                  <span className="text-xs font-mono" style={{ color: "oklch(0.35 0.01 240)" }}>·</span>
                  <span className="text-xs font-mono" style={{ color: "oklch(0.45 0.01 240)" }}>OBSIDIA</span>
                </div>
              )}
            </div>
          </SidebarHeader>

          <SidebarContent className="gap-0 py-2">
            {/* ─── Navigation principale ─── */}
            <div className="px-2 mb-1">
              {!isCollapsed && (
                <div className="text-xs font-mono uppercase tracking-widest px-2 py-1.5" style={{ color: "oklch(0.38 0.01 240)" }}>
                  Navigation
                </div>
              )}
              <SidebarMenu>
                {MAIN_NAV.map(item => {
                  const isActive = location === item.path || (item.path === "/mission" && location === "/");
                  return (
                    <SidebarMenuItem key={item.path}>
                      <SidebarMenuButton
                        isActive={isActive}
                        onClick={() => setLocation(item.path)}
                        tooltip={item.label}
                        className="h-9 transition-all font-normal"
                        style={isActive ? {
                          background: "oklch(0.72 0.18 145 / 0.12)",
                          color: "oklch(0.72 0.18 145)",
                        } : { color: "oklch(0.65 0.01 240)" }}
                      >
                        <item.icon className="h-4 w-4 shrink-0" />
                        <span className="text-sm">{item.label}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </div>

            {/* ─── Séparateur ─── */}
            <div className="mx-3 my-1" style={{ borderTop: "1px solid oklch(0.15 0.01 240)" }} />

            {/* ─── Mondes ─── */}
            <div className="px-2 mb-1">
              {!isCollapsed && (
                <div className="text-xs font-mono uppercase tracking-widest px-2 py-1.5" style={{ color: "oklch(0.38 0.01 240)" }}>
                  Mondes
                </div>
              )}
              <SidebarMenu>
                {WORLD_NAV.map(item => {
                  const isActive = location === item.path;
                  return (
                    <SidebarMenuItem key={item.path}>
                      <SidebarMenuButton
                        isActive={isActive}
                        onClick={() => setLocation(item.path)}
                        tooltip={item.label}
                        className="h-9 transition-all font-normal"
                        style={isActive ? {
                          background: `${item.color} / 0.10`,
                          color: item.color,
                        } : { color: "oklch(0.55 0.01 240)" }}
                      >
                        <item.icon className="h-4 w-4 shrink-0" style={isActive ? { color: item.color } : {}} />
                        <span className="text-sm">{item.label}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </div>

            {/* ─── Séparateur ─── */}
            <div className="mx-3 my-1" style={{ borderTop: "1px solid oklch(0.15 0.01 240)" }} />

            {/* ─── Outils (collapsible) ─── */}
            <div className="px-2">
              {!isCollapsed ? (
                <button
                  onClick={() => setToolsOpen(v => !v)}
                  className="flex items-center justify-between w-full px-2 py-1.5 rounded transition-colors"
                  style={{ color: "oklch(0.38 0.01 240)" }}
                >
                  <span className="text-xs font-mono uppercase tracking-widest">Outils</span>
                  <ChevronDown className={`h-3 w-3 transition-transform ${toolsOpen ? "rotate-180" : ""}`} />
                </button>
              ) : null}
              {(toolsOpen || isCollapsed) && (
                <SidebarMenu>
                  {TOOL_NAV.map(item => {
                    const isActive = location === item.path;
                    return (
                      <SidebarMenuItem key={item.path}>
                        <SidebarMenuButton
                          isActive={isActive}
                          onClick={() => setLocation(item.path)}
                          tooltip={item.label}
                          className="h-8 transition-all font-normal"
                          style={isActive ? {
                            background: "oklch(0.72 0.18 145 / 0.08)",
                            color: "oklch(0.72 0.18 145)",
                          } : { color: "oklch(0.45 0.01 240)" }}
                        >
                          <item.icon className="h-3.5 w-3.5 shrink-0" />
                          <span className="text-xs">{item.label}</span>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    );
                  })}
                </SidebarMenu>
              )}
            </div>
          </SidebarContent>

          {/* Footer utilisateur */}
          <SidebarFooter className="p-3" style={{ borderTop: "1px solid oklch(0.14 0.01 240)" }}>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-3 rounded-lg px-1 py-1 hover:bg-accent/20 transition-colors w-full text-left focus:outline-none">
                  <Avatar className="h-8 w-8 shrink-0" style={{ border: "1px solid oklch(0.22 0.01 240)" }}>
                    <AvatarFallback className="text-xs font-mono" style={{ background: "oklch(0.14 0.01 240)", color: "oklch(0.72 0.18 145)" }}>
                      {user?.name?.charAt(0).toUpperCase() ?? "?"}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0 group-data-[collapsible=icon]:hidden">
                    <p className="text-xs font-medium truncate leading-none" style={{ color: "oklch(0.75 0.01 240)" }}>
                      {user?.name || "—"}
                    </p>
                    <p className="text-xs truncate mt-1" style={{ color: "oklch(0.42 0.01 240)" }}>
                      {user?.email || "—"}
                    </p>
                  </div>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem
                  onClick={logout}
                  className="cursor-pointer text-destructive focus:text-destructive"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Déconnexion</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarFooter>
        </Sidebar>

        {/* Resize handle */}
        <div
          className={`absolute top-0 right-0 w-1 h-full cursor-col-resize transition-colors ${isCollapsed ? "hidden" : ""}`}
          onMouseDown={() => { if (!isCollapsed) setIsResizing(true); }}
          style={{ zIndex: 50 }}
        />
      </div>

      <SidebarInset>
        {isMobile && (
          <div className="flex border-b h-12 items-center justify-between px-3 sticky top-0 z-40"
            style={{ background: "oklch(0.09 0.01 240)", borderColor: "oklch(0.15 0.01 240)" }}>
            <div className="flex items-center gap-2">
              <SidebarTrigger className="h-8 w-8 rounded-lg" />
              <span className="text-sm font-mono" style={{ color: "oklch(0.72 0.18 145)" }}>
                {activeMain?.label ?? "OS4"}
              </span>
            </div>
          </div>
        )}
        <main className="flex-1 p-4">{children}</main>
      </SidebarInset>
    </>
  );
}
