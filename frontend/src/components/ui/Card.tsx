import React from 'react';
import { cn } from '../../lib/utils';
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  as?: keyof JSX.IntrinsicElements;
}
export function Card({ className, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800 shadow-soft',
        className
      )}
      {...props}>
      
      {children}
    </div>);

}
export function CardHeader({
  title,
  subtitle,
  action,
  className





}: {title: string;subtitle?: string;action?: React.ReactNode;className?: string;}) {
  return (
    <div
      className={cn(
        'flex items-start justify-between gap-4 px-5 pt-5',
        className
      )}>
      
      <div>
        <h3 className="font-display font-bold text-slate-800 dark:text-slate-100">
          {title}
        </h3>
        {subtitle &&
        <p className="text-sm text-slate-400 dark:text-slate-500 mt-0.5">
            {subtitle}
          </p>
        }
      </div>
      {action}
    </div>);

}