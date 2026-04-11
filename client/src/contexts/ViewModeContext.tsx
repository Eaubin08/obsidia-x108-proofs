import { createContext, useContext, useState, useEffect, ReactNode } from "react";

export type ViewMode = "simple" | "expert";

interface ViewModeContextType {
  mode: ViewMode;
  isSimple: boolean;
  isExpert: boolean;
  setMode: (mode: ViewMode) => void;
  toggle: () => void;
}

const ViewModeContext = createContext<ViewModeContextType>({
  mode: "expert",
  isSimple: false,
  isExpert: true,
  setMode: () => {},
  toggle: () => {},
});

export function ViewModeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ViewMode>(() => {
    try {
      const stored = localStorage.getItem("obsidia_mode");
      return (stored === "simple" || stored === "expert") ? stored : "expert";
    } catch {
      return "expert";
    }
  });

  const setMode = (newMode: ViewMode) => {
    setModeState(newMode);
    try {
      localStorage.setItem("obsidia_mode", newMode);
    } catch {}
  };

  const toggle = () => setMode(mode === "simple" ? "expert" : "simple");

  return (
    <ViewModeContext.Provider value={{
      mode,
      isSimple: mode === "simple",
      isExpert: mode === "expert",
      setMode,
      toggle,
    }}>
      {children}
    </ViewModeContext.Provider>
  );
}

export function useViewMode() {
  return useContext(ViewModeContext);
}

// Helper component for conditional rendering
export function SimpleView({ children }: { children: ReactNode }) {
  const { isSimple } = useViewMode();
  return isSimple ? <>{children}</> : null;
}

export function ExpertView({ children }: { children: ReactNode }) {
  const { isExpert } = useViewMode();
  return isExpert ? <>{children}</> : null;
}
