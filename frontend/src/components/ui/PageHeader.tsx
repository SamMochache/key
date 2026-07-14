import React from 'react';
export function PageHeader({
  title,
  description,
  actions




}: {title: string;description?: string;actions?: React.ReactNode;}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6">
      <div>
        <h1 className="font-display text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          {title}
        </h1>
        {description &&
        <p className="text-slate-500 dark:text-slate-400 mt-1.5 max-w-2xl">
            {description}
          </p>
        }
      </div>
      {actions &&
      <div className="flex items-center gap-2 shrink-0">{actions}</div>
      }
    </div>);

}