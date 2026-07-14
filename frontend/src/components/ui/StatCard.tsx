import React from 'react';
import * as Icons from 'lucide-react';
import { TrendingUpIcon, TrendingDownIcon } from 'lucide-react';
import { Card } from './Card';
import { cn } from '../../lib/utils';
type Tone = 'brand' | 'emerald' | 'warm' | 'rose';
const toneMap: Record<Tone, string> = {
  brand: 'bg-brand-50 text-brand-600 dark:bg-brand-600/20 dark:text-brand-300',
  emerald:
  'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-300',
  warm: 'bg-warm-50 text-warm-600 dark:bg-warm-500/20 dark:text-warm-300',
  rose: 'bg-rose-50 text-rose-600 dark:bg-rose-500/20 dark:text-rose-300'
};
export function StatCard({
  label,
  value,
  icon,
  tone = 'brand',
  delta,
  hint







}: {label: string;value: string | number;icon: string;tone?: Tone;delta?: number;hint?: string;}) {
  const Icon = (Icons as any)[icon] ?? Icons.Circle;
  const up = (delta ?? 0) >= 0;
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <span
          className={cn(
            'flex h-11 w-11 items-center justify-center rounded-2xl',
            toneMap[tone]
          )}>
          
          <Icon className="h-5 w-5" />
        </span>
        {delta !== undefined &&
        <span
          className={cn(
            'inline-flex items-center gap-1 text-xs font-bold rounded-full px-2 py-0.5',
            up ?
            'text-emerald-600 bg-emerald-50 dark:bg-emerald-500/15' :
            'text-rose-600 bg-rose-50 dark:bg-rose-500/15'
          )}>
          
            {up ?
          <TrendingUpIcon className="h-3 w-3" /> :

          <TrendingDownIcon className="h-3 w-3" />
          }
            {Math.abs(delta)}%
          </span>
        }
      </div>
      <p className="mt-4 text-3xl font-display font-extrabold text-slate-900 dark:text-white tracking-tight">
        {value}
      </p>
      <p className="text-sm font-semibold text-slate-500 dark:text-slate-400 mt-0.5">
        {label}
      </p>
      {hint && <p className="text-xs text-slate-400 mt-1">{hint}</p>}
    </Card>);

}