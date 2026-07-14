import React from 'react';
import { PlusIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { UpcomingEventsCard } from '../components/widgets/Widgets';
import { events } from '../lib/data';
import { cn } from '../lib/utils';
const eventByDay: Record<
  number,
  {
    label: string;
    tone: string;
  }[]> =
{
  15: [
  {
    label: 'Term 2 Assessments',
    tone: 'bg-rose-500'
  }],

  16: [
  {
    label: 'Assessments',
    tone: 'bg-rose-500'
  }],

  17: [
  {
    label: 'Gardens Trip',
    tone: 'bg-warm-500'
  }],

  19: [
  {
    label: 'Sports Day',
    tone: 'bg-emerald-500'
  }],

  22: [
  {
    label: 'PTA Meeting',
    tone: 'bg-brand-500'
  }],

  24: [
  {
    label: 'Conferences',
    tone: 'bg-brand-500'
  }]

};
export function Calendar() {
  const days = Array.from(
    {
      length: 31
    },
    (_, i) => i + 1
  );
  const today = 14;
  return (
    <div>
      <PageHeader
        title="Academic Calendar"
        description="Exams, sports, trips, meetings and holidays — the rhythm of the school year."
        actions={
        <Button>
            <PlusIcon className="h-4 w-4" /> Add event
          </Button>
        } />
      

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display text-xl font-extrabold text-slate-900 dark:text-white">
                July 2026
              </h2>
              <div className="flex gap-2">
                {['Exams', 'Sports', 'Trips', 'Meetings'].map((l, i) =>
                <span
                  key={l}
                  className="flex items-center gap-1.5 text-xs font-medium text-slate-500">
                  
                    <span
                    className={cn(
                      'h-2 w-2 rounded-full',
                      [
                      'bg-rose-500',
                      'bg-emerald-500',
                      'bg-warm-500',
                      'bg-brand-500'][
                      i]
                    )} />
                  
                    {l}
                  </span>
                )}
              </div>
            </div>
            <div className="grid grid-cols-7 gap-2 text-center text-xs font-bold text-slate-400 mb-2">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((d) =>
              <span key={d}>{d}</span>
              )}
            </div>
            <div className="grid grid-cols-7 gap-2">
              {Array.from({
                length: 2
              }).map((_, i) =>
              <span key={`p${i}`} />
              )}
              {days.map((d) => {
                const evts = eventByDay[d] ?? [];
                const isToday = d === today;
                return (
                  <div
                    key={d}
                    className={cn(
                      'min-h-[68px] rounded-2xl border p-1.5 text-left',
                      isToday ?
                      'border-brand-500 bg-brand-50 dark:bg-brand-600/15' :
                      'border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/60'
                    )}>
                    
                    <span
                      className={cn(
                        'text-xs font-bold',
                        isToday ?
                        'text-brand-600' :
                        'text-slate-500 dark:text-slate-400'
                      )}>
                      
                      {d}
                    </span>
                    <div className="mt-1 space-y-1">
                      {evts.map((e, i) =>
                      <div
                        key={i}
                        className={cn(
                          'rounded-md px-1.5 py-0.5 text-[10px] font-semibold text-white truncate',
                          e.tone
                        )}>
                        
                          {e.label}
                        </div>
                      )}
                    </div>
                  </div>);

              })}
            </div>
          </Card>
        </div>
        <UpcomingEventsCard />
      </div>
    </div>);

}