import React from 'react';
import { cn } from '../../lib/utils';
import { initials } from '../../lib/utils';
export function Avatar({
  src,
  name,
  size = 40,
  className,
  ring






}: {src?: string;name: string;size?: number;className?: string;ring?: boolean;}) {
  return (
    <div
      className={cn(
        'relative shrink-0 overflow-hidden rounded-full bg-brand-100 dark:bg-brand-600/30 flex items-center justify-center',
        ring && 'ring-2 ring-white dark:ring-slate-900',
        className
      )}
      style={{
        width: size,
        height: size
      }}
      aria-hidden={!!src}>
      
      {src ?
      <img src={src} alt={name} className="h-full w-full object-cover" /> :

      <span className="text-xs font-bold text-brand-700 dark:text-brand-200">
          {initials(name)}
        </span>
      }
    </div>);

}