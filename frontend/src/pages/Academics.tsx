import React from 'react';
import * as Icons from 'lucide-react';
import { TargetIcon, EyeIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { subjects } from '../lib/data';
import { cn } from '../lib/utils';
const tone: Record<string, string> = {
  brand: 'bg-brand-50 text-brand-600 dark:bg-brand-600/20 dark:text-brand-300',
  emerald:
  'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-300',
  warm: 'bg-warm-50 text-warm-600 dark:bg-warm-500/20 dark:text-warm-300'
};
const learningGoals = [
'Develops concentration through the full work cycle',
'Builds independence and care for the environment',
'Grows language through phonetic and expressive work',
'Explores mathematics with concrete materials'];

const observations = [
{
  student: 'Mia Chen',
  note: 'Chose the pink tower independently and repeated the work three times.',
  by: 'Sophie L.'
},
{
  student: 'Noah Bennett',
  note: 'Showing readiness for the moveable alphabet.',
  by: 'Marcus R.'
},
{
  student: 'Aria Kapoor',
  note: 'Extended pouring work into a self-directed practical challenge.',
  by: 'Priya N.'
}];

export function Academics() {
  return (
    <div>
      <PageHeader
        title="Academics"
        description="Montessori learning areas, lessons, and the observations that guide each child’s path." />
      

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {subjects.map((s) => {
          const Icon = (Icons as any)[s.icon] ?? Icons.BookOpen;
          return (
            <Card
              key={s.id}
              className="p-5 hover:-translate-y-0.5 transition-transform">
              
              <div className="flex items-center gap-3">
                <span
                  className={cn(
                    'flex h-12 w-12 items-center justify-center rounded-2xl',
                    tone[s.color]
                  )}>
                  
                  <Icon className="h-5 w-5" />
                </span>
                <div>
                  <h3 className="font-display font-bold text-slate-800 dark:text-slate-100">
                    {s.name}
                  </h3>
                  <p className="text-xs text-slate-400">
                    {s.lessons} lessons · continuous assessment
                  </p>
                </div>
              </div>
            </Card>);

        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader
            title="Montessori Learning Goals"
            action={<TargetIcon className="h-5 w-5 text-emerald-500" />} />
          
          <div className="px-5 pb-5 mt-2 space-y-3">
            {learningGoals.map((g, i) =>
            <div key={i} className="flex items-start gap-3">
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-emerald-50 dark:bg-emerald-500/15 text-emerald-600 text-xs font-bold">
                  {i + 1}
                </span>
                <p className="text-sm text-slate-600 dark:text-slate-300">
                  {g}
                </p>
              </div>
            )}
          </div>
        </Card>

        <Card>
          <CardHeader
            title="Recent Teacher Observations"
            action={<EyeIcon className="h-5 w-5 text-slate-300" />} />
          
          <div className="px-5 pb-5 mt-2 space-y-4">
            {observations.map((o, i) =>
            <div
              key={i}
              className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-3.5">
              
                <div className="flex items-center justify-between mb-1">
                  <p className="font-semibold text-sm text-slate-800 dark:text-slate-100">
                    {o.student}
                  </p>
                  <Badge tone="brand">{o.by}</Badge>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-300">
                  {o.note}
                </p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>);

}