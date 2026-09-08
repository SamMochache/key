import React, { useEffect, useState, useRef } from 'react';
import { MenuIcon, BellIcon, SunIcon, MoonIcon, ChevronDownIcon, SettingsIcon, LogOutIcon, UserIcon, Loader2Icon } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { useApp } from '../../context/AppContext';
import { Avatar } from '../ui/Avatar';
import { GlobalSearch } from './GlobalSearch';
import { cn } from '../../lib/utils';
import { listNotifications, markAllNotificationsRead, markNotificationRead, type NotificationItem } from '../../lib/notificationsApi';

const ROLE_LABELS: Record<string, string> = {
  admin: 'Administrator',
  teacher: 'Teacher',
  parent: 'Parent',
  student: 'Student',
};

function useOutside(cb: () => void) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => { const h = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) cb(); }; document.addEventListener('mousedown', h); return () => document.removeEventListener('mousedown', h); }, [cb]);
  return ref;
}

export function Topbar({ onMenu }: { onMenu: () => void }) {
  const { role, user, logout, dark, toggleDark } = useApp();
  const [notifOpen, setNotifOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifLoading, setNotifLoading] = useState(false);
  const [notifError, setNotifError] = useState('');
  const notifRef = useOutside(() => setNotifOpen(false));
  const menuRef = useOutside(() => setMenuOpen(false));
  const displayName = user?.full_name || user?.email || 'KEY user';
  const profilePhoto = (user as (typeof user & { profile_photo?: string | null }))?.profile_photo || undefined;

  const loadNotifications = () => {
    setNotifLoading(true); setNotifError('');
    listNotifications().then(data => { setNotifications(data.results); setUnreadCount(data.unread_count); }).catch(err => setNotifError(err instanceof Error ? err.message : 'Unable to load notifications.')).finally(() => setNotifLoading(false));
  };
  useEffect(() => { loadNotifications(); const timer = window.setInterval(loadNotifications, 30000); return () => window.clearInterval(timer); }, []);

  const markRead = async (id: string) => { try { await markNotificationRead(id); setNotifications(items => items.map(item => item.id === id ? { ...item, is_read: true } : item)); setUnreadCount(count => Math.max(0, count - 1)); } catch (err) { setNotifError(err instanceof Error ? err.message : 'Unable to update notification.'); } };
  const markAllRead = async () => { try { await markAllNotificationsRead(); setNotifications(items => items.map(item => ({ ...item, is_read: true }))); setUnreadCount(0); } catch (err) { setNotifError(err instanceof Error ? err.message : 'Unable to update notifications.'); } };

  return <header className="sticky top-0 z-20 h-16 flex items-center gap-3 px-4 lg:px-6 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-b border-slate-200/70 dark:border-slate-800">
    <button onClick={onMenu} className="lg:hidden rounded-xl p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800" aria-label="Open menu"><MenuIcon className="h-5 w-5" /></button>
    <div className="flex-1 max-w-xs"><GlobalSearch /></div>
    <div className="ml-auto flex items-center gap-1.5">
      <button onClick={toggleDark} className="rounded-xl p-2.5 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 dark:text-slate-400" aria-label="Toggle dark mode">{dark ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}</button>
      <div className="relative" ref={notifRef}>
        <button onClick={() => { setNotifOpen(o => !o); if (!notifOpen) loadNotifications(); }} className="relative rounded-xl p-2.5 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 dark:text-slate-400" aria-label="Notifications">
          <BellIcon className="h-5 w-5" />{unreadCount > 0 && <span className="absolute -top-0.5 -right-0.5 min-w-4 h-4 px-1 rounded-full bg-warm-500 text-white text-[9px] font-bold flex items-center justify-center ring-2 ring-white dark:ring-slate-900">{unreadCount > 99 ? '99+' : unreadCount}</span>}
        </button>
        <AnimatePresence>{notifOpen && <motion.div initial={{ opacity: 0, y: 6, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 6, scale: .98 }} className="absolute right-0 mt-2 w-80 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-softlg overflow-hidden">
          <div className="px-5 py-3.5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between"><p className="font-display font-bold text-slate-800 dark:text-slate-100">Notifications</p><button onClick={markAllRead} disabled={!unreadCount} className="text-xs font-semibold text-brand-600 disabled:text-slate-300">Mark all read</button></div>
          <div className="max-h-80 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800">
            {notifLoading ? <div className="p-8 flex justify-center"><Loader2Icon className="h-5 w-5 animate-spin text-brand-600" /></div> : notifError ? <p className="p-5 text-sm text-rose-600">{notifError}</p> : notifications.length === 0 ? <p className="p-7 text-sm text-slate-400 text-center">You're all caught up.</p> : notifications.map(item => <button key={item.id} onClick={() => { if (!item.is_read) markRead(item.id); if (item.link) window.location.href = item.link; }} className={cn('w-full text-left flex gap-3 px-5 py-3.5 hover:bg-slate-50 dark:hover:bg-slate-800/60', !item.is_read && 'bg-brand-50/40 dark:bg-brand-500/5')}><span className="mt-1 h-8 w-8 shrink-0 rounded-xl bg-brand-50 dark:bg-slate-800 flex items-center justify-center text-brand-600"><BellIcon className="h-4 w-4" /></span><span className="min-w-0"><span className="block text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">{item.title}</span><span className="block text-xs text-slate-400 mt-0.5 truncate">{item.body || new Date(item.created_at).toLocaleString()}</span></span></button>)}
          </div>
        </motion.div>}</AnimatePresence>
      </div>
      <div className="relative pl-1" ref={menuRef}><button onClick={() => setMenuOpen(o => !o)} className="flex items-center gap-2 rounded-2xl p-1 pr-2 hover:bg-slate-100 dark:hover:bg-slate-800"><Avatar src={profilePhoto} name={displayName} size={34} ring /><span className="hidden sm:block text-left leading-tight"><span className="block text-sm font-bold text-slate-800 dark:text-slate-100">{displayName}</span><span className="block text-[11px] text-slate-400">{ROLE_LABELS[role] || role}</span></span><ChevronDownIcon className="h-4 w-4 text-slate-400 hidden sm:block" /></button>
        <AnimatePresence>{menuOpen && <motion.div initial={{ opacity: 0, y: 6, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 6, scale: .98 }} className="absolute right-0 mt-2 w-72 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-softlg overflow-hidden"><div className="flex items-center gap-3 px-5 py-4 border-b border-slate-100 dark:border-slate-800"><Avatar src={profilePhoto} name={displayName} size={44} /><div className="min-w-0"><p className="font-bold text-slate-800 dark:text-slate-100 truncate">{displayName}</p><p className="text-xs text-slate-400 truncate">{ROLE_LABELS[role] || role}</p></div></div><div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800"><p className="px-2 py-1 text-[11px] font-bold uppercase tracking-wider text-slate-400">Signed in as</p><p className="px-2 py-1 text-sm text-slate-600 dark:text-slate-300 truncate">{user?.email}</p></div><div className="px-3 pb-3 pt-2 space-y-0.5"><MenuRow icon={<UserIcon className="h-4 w-4" />} label="My Profile" /><MenuRow icon={<SettingsIcon className="h-4 w-4" />} label="Settings" /><MenuRow icon={<LogOutIcon className="h-4 w-4" />} label="Sign out" danger onClick={logout} /></div></motion.div>}</AnimatePresence>
      </div>
    </div>
  </header>;
}
function MenuRow({ icon, label, danger, onClick }: { icon: React.ReactNode; label: string; danger?: boolean; onClick?: () => void }) { return <button onClick={onClick} className={cn('w-full flex items-center gap-3 rounded-2xl px-3 py-2 text-sm font-semibold transition-colors', danger ? 'text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-500/10' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800')}>{icon}{label}</button>; }
