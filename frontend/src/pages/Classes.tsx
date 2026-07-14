import React from 'react';
import { UsersIcon, ArrowRightIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { classes } from '../lib/data';
import { cn } from '../lib/utils';
const accent: Record<string, string> = {
  brand: 'bg-brand-600',
  emerald: 'bg-emerald-500',
  warm: 'bg-warm-500'
};
export function Classes() {
  return (
    <div>
      <PageHeader
        title="Classes"
        description="Our learning communities — each a prepared environment where children flourish together." />
      

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.map((c) =>
        <Card
          key={c.id}
          className="overflow-hidden hover:-translate-y-1 transition-transform">
          
            <div className={cn('h-2', accent[c.color])} />
            <div className="p-5">
              <div className="flex items-center justify-between">
                <h3 className="font-display text-lg font-extrabold text-slate-900 dark:text-white">
                  {c.name} Class
                </h3>
                <Badge tone="slate">{c.ageGroup}</Badge>
              </div>
              <div className="flex items-center gap-2 mt-3">
                <Avatar src={c.teacherAvatar} name={c.teacher} size={30} />
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  Guided by {c.teacher}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-2 mt-5 text-center">
                <Stat value={String(c.students)} label="Students" />
                <Stat value="6" label="Subjects" />
                <Stat value="94%" label="Attend." />
              </div>

              <button className="mt-5 w-full inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-100 dark:bg-slate-800 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-200/70 dark:hover:bg-slate-700 transition-colors">
                Open class <ArrowRightIcon className="h-4 w-4" />
              </button>
            </div>
          </Card>
        )}
      </div>
    </div>);

}
function Stat({ value, label }: {value: string;label: string;}) {
  return (
    <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 py-2.5">
      <p className="font-display font-extrabold text-slate-800 dark:text-slate-100">
        {value}
      </p>
      <p className="text-[11px] text-slate-400 font-medium">{label}</p>
    </div>);

}