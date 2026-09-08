import React, {
  useCallback,
  useEffect,
  useState,
  createContext,
  useContext
} from 'react';
import type { Role } from '../lib/types';
import {
  clearTokens,
  getAccessToken,
  getCurrentUser,
  getMySchool,
  type CurrentUser,
  type School
} from '../lib/api';

export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';
export type SchoolStatus = 'idle' | 'loading' | 'loaded' | 'unavailable' | 'error';

interface AppState {
  role: Role;
  user: CurrentUser | null;
  school: School | null;
  schoolStatus: SchoolStatus;
  authStatus: AuthStatus;
  refreshSession: () => Promise<void>;
  logout: () => void;
  dark: boolean;
  toggleDark: () => void;
}

const AppContext = createContext<AppState | null>(null);
const supportedRoles: Role[] = ['admin', 'teacher', 'parent', 'student'];

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [role, setRole] = useState<Role>('student');
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [school, setSchool] = useState<School | null>(null);
  const [schoolStatus, setSchoolStatus] = useState<SchoolStatus>('idle');
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
      setSchool(null);
      setSchoolStatus('idle');
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

      // Institution administrators, teachers, parents, and students all carry
      // school_id. Platform staff/superusers intentionally do not.
      if (currentUser.school_id) {
        setSchoolStatus('loading');
        try {
          const currentSchool = await getMySchool();
          setSchool(currentSchool);
          setSchoolStatus('loaded');
        } catch {
          setSchool(null);
          setSchoolStatus('error');
        }
      } else {
        setSchool(null);
        setSchoolStatus('unavailable');
      }

      setAuthStatus('authenticated');
    } catch (error) {
      clearTokens();
      setUser(null);
      setSchool(null);
      setSchoolStatus('idle');
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
    setSchool(null);
    setSchoolStatus('idle');
    setAuthStatus('unauthenticated');
  }, []);

  const toggleDark = useCallback(() => setDark((d) => !d), []);

  return (
    <AppContext.Provider value={{ role, user, school, schoolStatus, authStatus, refreshSession, logout, dark, toggleDark }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
