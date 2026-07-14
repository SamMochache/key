import React from 'react';
import { cn } from '../../lib/utils';
type Tone = 'brand' | 'emerald' | 'warm' | 'slate' | 'rose';
const tones: Record<Tone, string> = {
  brand: 'bg-brand-50 text-brand-700 dark:bg-brand-600/20 dark:text-brand-300',
  emerald:
  'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300',
  warm: 'bg-warm-50 text-warm-600 dark:bg-warm-500/20 dark:text-warm-300',
  slate: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300',
  rose: 'bg-rose-50 text-rose-600 dark:bg-rose-500/20 dark:text-rose-300'
};
export function Badge({
  tone = 'slate',
  className,
  children




}: {tone?: Tone;className?: string;children: React.ReactNode;}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold',
        tones[tone],
        className
      )}>
      
      {children}
    </span>);

}