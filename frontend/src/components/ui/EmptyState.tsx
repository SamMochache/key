import React from 'react';
import * as Icons from 'lucide-react';
export function EmptyState({
  icon = 'Inbox',
  title,
  description,
  action





}: {icon?: string;title: string;description?: string;action?: React.ReactNode;}) {
  const Icon = (Icons as any)[icon] ?? Icons.Inbox;
  return (
    <div className="flex flex-col items-center justify-center text-center py-14 px-6">
      <span className="flex h-16 w-16 items-center justify-center rounded-3xl bg-brand-50 dark:bg-slate-800 text-brand-500 mb-4">
        <Icon className="h-7 w-7" />
      </span>
      <h3 className="font-display font-bold text-slate-800 dark:text-slate-100">
        {title}
      </h3>
      {description &&
      <p className="text-sm text-slate-400 mt-1 max-w-sm">{description}</p>
      }
      {action && <div className="mt-5">{action}</div>}
    </div>);

}