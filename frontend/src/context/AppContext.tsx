import React, {
  useCallback,
  useEffect,
  useState,
  createContext,
  useContext
} from 'react';
import type { Role } from '../lib/types';
import { getAccessToken, getCurrentUser } from '../lib/api';

interface AppState {
  role: Role;
  setRole: (r: Role) => void;
  dark: boolean;
  toggleDark: () => void;
}

const AppContext = createContext<AppState | null>(null);

const supportedRoles: Role[] = ['admin', 'principal', 'teacher', 'parent', 'student'];

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [role, setRole] = useState<Role>('admin');
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    if (dark) root.classList.add('dark');
    else root.classList.remove('dark');
  }, [dark]);

  useEffect(() => {
    if (!getAccessToken()) return;

    let active = true;
    getCurrentUser()
      .then((user) => {
        if (!active) return;
        if (supportedRoles.includes(user.role as Role)) {
          setRole(user.role as Role);
        }
      })
      .catch(() => {
        // The prototype role remains active when there is no valid session.
      });

    return () => {
      active = false;
    };
  }, []);

  const toggleDark = useCallback(() => setDark((d) => !d), []);

  return (
    <AppContext.Provider value={{ role, setRole, dark, toggleDark }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
