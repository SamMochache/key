import React from 'react';
import { NavLink } from 'react-router-dom';
import * as Icons from 'lucide-react';
import { navGroups } from './nav';
import { useApp } from '../../context/AppContext';
import { LOGO_URL } from '../../lib/data';
import { cn } from '../../lib/utils';
function Icon({ name, className }: {name: string;className?: string;}) {
  const Cmp = (Icons as any)[name] ?? Icons.Circle;
  return <Cmp className={className} />;
}
export function Sidebar({
  open,
  onClose



}: {open: boolean;onClose: () => void;}) {
  const { role } = useApp();
  return (
    <>
      {open &&
      <div
        className="fixed inset-0 z-30 bg-slate-900/40 backdrop-blur-sm lg:hidden"
        onClick={onClose}
        aria-hidden />

      }
      <aside
        className={cn(
          'fixed z-40 inset-y-0 left-0 w-72 flex flex-col bg-white dark:bg-slate-900 border-r border-slate-200/70 dark:border-slate-800 transition-transform duration-300 lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}>
        
        <div className="flex items-center gap-3 px-5 h-16 shrink-0">
          <img
            src={LOGO_URL}
            alt=""
            className="h-9 w-9 rounded-xl object-contain bg-brand-50 dark:bg-slate-800 p-0.5" />
          
          <div className="leading-tight">
            <p className="font-display font-extrabold text-slate-800 dark:text-white text-[15px]">
              Key International
            </p>
            <p className="text-[11px] text-slate-400 dark:text-slate-500 font-medium tracking-wide">
              MONTESSORI SCHOOL
            </p>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 pb-6 space-y-6">
          {navGroups.map((group) => {
            const items = group.items.filter((i) => i.roles.includes(role));
            if (!items.length) return null;
            return (
              <div key={group.title}>
                <p className="px-3 mb-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-600">
                  {group.title}
                </p>
                <div className="space-y-0.5">
                  {items.map((item) =>
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.to === '/'}
                    onClick={onClose}
                    className={({ isActive }) =>
                    cn(
                      'group flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-semibold transition-colors',
                      isActive ?
                      'bg-brand-600 text-white shadow-soft' :
                      'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                    )
                    }>
                    
                      <Icon name={item.icon} className="h-[18px] w-[18px]" />
                      {item.label}
                    </NavLink>
                  )}
                </div>
              </div>);

          })}
        </nav>

        <div className="p-3">
          <div className="rounded-2xl bg-brand-50 dark:bg-slate-800 p-4">
            <p className="text-sm font-bold text-brand-800 dark:text-brand-200">
              Growth over grades
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Every child’s journey, observed with care.
            </p>
          </div>
        </div>
      </aside>
    </>);

}