import React, { useEffect, useState, useRef } from 'react';
import {
  MenuIcon,
  BellIcon,
  SunIcon,
  MoonIcon,
  ChevronDownIcon,
  CheckIcon,
  SettingsIcon,
  LogOutIcon,
  UserIcon } from
'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { useApp } from '../../context/AppContext';
import { PROFILES, ROLE_LABELS, announcements } from '../../lib/data';
import type { Role } from '../../lib/types';
import { Avatar } from '../ui/Avatar';
import { GlobalSearch } from './GlobalSearch';
import { cn } from '../../lib/utils';
const ROLES: Role[] = ['admin', 'principal', 'teacher', 'parent', 'student'];
function useOutside(cb: () => void) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) cb();
    };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, [cb]);
  return ref;
}
export function Topbar({ onMenu }: {onMenu: () => void;}) {
  const { role, setRole, dark, toggleDark } = useApp();
  const profile = PROFILES[role];
  const [notifOpen, setNotifOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const notifRef = useOutside(() => setNotifOpen(false));
  const menuRef = useOutside(() => setMenuOpen(false));
  return (
    <header className="sticky top-0 z-20 h-16 flex items-center gap-3 px-4 lg:px-6 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-b border-slate-200/70 dark:border-slate-800">
      <button
        onClick={onMenu}
        className="lg:hidden rounded-xl p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
        aria-label="Open menu">
        
        <MenuIcon className="h-5 w-5" />
      </button>

      <div className="flex-1 max-w-xs">
        <GlobalSearch />
      </div>

      <div className="ml-auto flex items-center gap-1.5">
        <button
          onClick={toggleDark}
          className="rounded-xl p-2.5 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 dark:text-slate-400"
          aria-label="Toggle dark mode">
          
          {dark ?
          <SunIcon className="h-5 w-5" /> :

          <MoonIcon className="h-5 w-5" />
          }
        </button>

        {/* Notifications */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setNotifOpen((o) => !o)}
            className="relative rounded-xl p-2.5 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 dark:text-slate-400"
            aria-label="Notifications">
            
            <BellIcon className="h-5 w-5" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-warm-500 ring-2 ring-white dark:ring-slate-900" />
          </button>
          <AnimatePresence>
            {notifOpen &&
            <motion.div
              initial={{
                opacity: 0,
                y: 6,
                scale: 0.98
              }}
              animate={{
                opacity: 1,
                y: 0,
                scale: 1
              }}
              exit={{
                opacity: 0,
                y: 6,
                scale: 0.98
              }}
              className="absolute right-0 mt-2 w-80 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-softlg overflow-hidden">
              
                <div className="px-5 py-3.5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                  <p className="font-display font-bold text-slate-800 dark:text-slate-100">
                    Notifications
                  </p>
                  <span className="text-xs font-semibold text-brand-600">
                    Mark all read
                  </span>
                </div>
                <div className="max-h-80 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800">
                  {announcements.map((a) =>
                <div
                  key={a.id}
                  className="flex gap-3 px-5 py-3.5 hover:bg-slate-50 dark:hover:bg-slate-800/60">
                  
                      <span className="mt-1 h-8 w-8 shrink-0 rounded-xl bg-brand-50 dark:bg-slate-800 flex items-center justify-center text-brand-600">
                        <BellIcon className="h-4 w-4" />
                      </span>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">
                          {a.title}
                        </p>
                        <p className="text-xs text-slate-400 mt-0.5">
                          {a.author} · {a.date}
                        </p>
                      </div>
                    </div>
                )}
                </div>
              </motion.div>
            }
          </AnimatePresence>
        </div>

        {/* Profile */}
        <div className="relative pl-1" ref={menuRef}>
          <button
            onClick={() => setMenuOpen((o) => !o)}
            className="flex items-center gap-2 rounded-2xl p-1 pr-2 hover:bg-slate-100 dark:hover:bg-slate-800">
            
            <Avatar src={profile.avatar} name={profile.name} size={34} ring />
            <span className="hidden sm:block text-left leading-tight">
              <span className="block text-sm font-bold text-slate-800 dark:text-slate-100">
                {profile.name}
              </span>
              <span className="block text-[11px] text-slate-400">
                {ROLE_LABELS[role]}
              </span>
            </span>
            <ChevronDownIcon className="h-4 w-4 text-slate-400 hidden sm:block" />
          </button>
          <AnimatePresence>
            {menuOpen &&
            <motion.div
              initial={{
                opacity: 0,
                y: 6,
                scale: 0.98
              }}
              animate={{
                opacity: 1,
                y: 0,
                scale: 1
              }}
              exit={{
                opacity: 0,
                y: 6,
                scale: 0.98
              }}
              className="absolute right-0 mt-2 w-72 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-softlg overflow-hidden">
              
                <div className="flex items-center gap-3 px-5 py-4 border-b border-slate-100 dark:border-slate-800">
                  <Avatar src={profile.avatar} name={profile.name} size={44} />
                  <div className="min-w-0">
                    <p className="font-bold text-slate-800 dark:text-slate-100 truncate">
                      {profile.name}
                    </p>
                    <p className="text-xs text-slate-400 truncate">
                      {profile.title}
                    </p>
                  </div>
                </div>
                <div className="px-3 py-2">
                  <p className="px-2 py-1 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    View as role
                  </p>
                  {ROLES.map((r) =>
                <button
                  key={r}
                  onClick={() => {
                    setRole(r);
                    setMenuOpen(false);
                  }}
                  className={cn(
                    'w-full flex items-center gap-3 rounded-2xl px-3 py-2 text-sm font-semibold transition-colors',
                    r === role ?
                    'bg-brand-50 dark:bg-slate-800 text-brand-700 dark:text-brand-300' :
                    'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                  )}>
                  
                      <Avatar
                    src={PROFILES[r].avatar}
                    name={PROFILES[r].name}
                    size={26} />
                  
                      {ROLE_LABELS[r]}
                      {r === role &&
                  <CheckIcon className="h-4 w-4 ml-auto text-brand-600" />
                  }
                    </button>
                )}
                </div>
                <div className="px-3 pb-3 border-t border-slate-100 dark:border-slate-800 pt-2 space-y-0.5">
                  <MenuRow
                  icon={<UserIcon className="h-4 w-4" />}
                  label="My Profile" />
                
                  <MenuRow
                  icon={<SettingsIcon className="h-4 w-4" />}
                  label="Settings" />
                
                  <MenuRow
                  icon={<LogOutIcon className="h-4 w-4" />}
                  label="Sign out"
                  danger />
                
                </div>
              </motion.div>
            }
          </AnimatePresence>
        </div>
      </div>
    </header>);

}
function MenuRow({
  icon,
  label,
  danger




}: {icon: React.ReactNode;label: string;danger?: boolean;}) {
  return (
    <button
      className={cn(
        'w-full flex items-center gap-3 rounded-2xl px-3 py-2 text-sm font-semibold transition-colors',
        danger ?
        'text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-500/10' :
        'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
      )}>
      
      {icon}
      {label}
    </button>);

}