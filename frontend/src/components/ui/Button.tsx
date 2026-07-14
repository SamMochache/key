import React from 'react';
import { cn } from '../../lib/utils';
type Variant = 'primary' | 'secondary' | 'ghost' | 'emerald';
const variants: Record<Variant, string> = {
  primary: 'bg-brand-600 text-white hover:bg-brand-700 shadow-soft',
  emerald: 'bg-emerald-500 text-white hover:bg-emerald-600 shadow-soft',
  secondary:
  'bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800',
  ghost:
  'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
};
interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}
export function Button({
  variant = 'primary',
  className,
  children,
  ...props
}: Props) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-2xl px-4 py-2.5 text-sm font-semibold transition-colors disabled:opacity-50 disabled:pointer-events-none',
        variants[variant],
        className
      )}
      {...props}>
      
      {children}
    </button>);

}