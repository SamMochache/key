import React, {
  useCallback,
  useEffect,
  useState,
  createContext,
  useContext
} from 'react';
import type { Role } from '../lib/types';
import { clearTokens, getAccessToken, getCurrentUser, type CurrentUser } from '../lib/api';

export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

interface AppState {
  role: Role;
  user: CurrentUser | null;
  authStatus: AuthStatus;
  refreshSession: () => Promise<void>;
  logout: () => void;
  dark: boolean;
  toggleDark: () => void;
}

const AppContext = createContext<AppState | null>(null);
const supportedRoles: Role[] = ['admin', 'teacher', 'student'];

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [role, setRole] = useState<Role>('student');
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [authStatus, setAuthStatus] = useState<AuthStatus>('loading');
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    if (dark) root.classList.add('dark');
    else root.classList.remove('dark');
  }, [dark]);

  const refreshSession = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setUser(null);
      setAuthStatus('unauthenticated');
      return;
    }

    setAuthStatus('loading');
    try {
      const currentUser = await getCurrentUser();
      if (!supportedRoles.includes(currentUser.role as Role)) {
        throw new Error('This account does not have a supported application role.');
      }
      setUser(currentUser);
      setRole(currentUser.role as Role);
      setAuthStatus('authenticated');
    } catch (error) {
      clearTokens();
      setUser(null);
      setAuthStatus('unauthenticated');
      throw error;
    }
  }, []);

  useEffect(() => {
    refreshSession().catch(() => undefined);
  }, [refreshSession]);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
    setAuthStatus('unauthenticated');
  }, []);

  const toggleDark = useCallback(() => setDark((d) => !d), []);

  return (
    <AppContext.Provider value={{ role, user, authStatus, refreshSession, logout, dark, toggleDark }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
