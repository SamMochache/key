import React, {
  useCallback,
  useEffect,
  useState,
  createContext,
  useContext } from
'react';
import type { Role } from '../lib/types';
interface AppState {
  role: Role;
  setRole: (r: Role) => void;
  dark: boolean;
  toggleDark: () => void;
}
const AppContext = createContext<AppState | null>(null);
export function AppProvider({ children }: {children: React.ReactNode;}) {
  const [role, setRole] = useState<Role>('admin');
  const [dark, setDark] = useState(false);
  useEffect(() => {
    const root = document.documentElement;
    if (dark) root.classList.add('dark');else
    root.classList.remove('dark');
  }, [dark]);
  const toggleDark = useCallback(() => setDark((d) => !d), []);
  return (
    <AppContext.Provider
      value={{
        role,
        setRole,
        dark,
        toggleDark
      }}>
      
      {children}
    </AppContext.Provider>);

}
export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}