import React, { useState } from 'react';
import {
  CheckIcon,
  XIcon,
  ClockIcon,
  ShieldCheckIcon,
  SaveIcon } from
'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Avatar } from '../components/ui/Avatar';
import { StatCard } from '../components/ui/StatCard';
import { AttendanceAreaChart } from '../components/charts/Charts';
import { students } from '../lib/data';
import { cn } from '../lib/utils';
type Status = 'present' | 'absent' | 'late' | 'excused';
const options: {
  key: Status;
  label: string;
  icon: React.ReactNode;
  active: string;
}[] = [
{
  key: 'present',
  label: 'Present',
  icon: <CheckIcon className="h-4 w-4" />,
  active: 'bg-emerald-500 text-white'
},
{
  key: 'late',
  label: 'Late',
  icon: <ClockIcon className="h-4 w-4" />,
  active: 'bg-warm-500 text-white'
},
{
  key: 'absent',
  label: 'Absent',
  icon: <XIcon className="h-4 w-4" />,
  active: 'bg-rose-500 text-white'
},
{
  key: 'excused',
  label: 'Excused',
  icon: <ShieldCheckIcon className="h-4 w-4" />,
  active: 'bg-brand-600 text-white'
}];

export function Attendance() {
  const roster = students.filter((s) => s.status === 'Enrolled');
  const [marks, setMarks] = useState<Record<string, Status>>(
    Object.fromEntries(roster.map((s) => [s.id, 'present']))
  );
  const counts = roster.reduce(
    (acc, s) => {
      acc[marks[s.id]]++;
      return acc;
    },
    {
      present: 0,
      absent: 0,
      late: 0,
      excused: 0
    } as Record<Status, number>
  );
  return (
    <div>
      <PageHeader
        title="Attendance"
        description="Mark today’s Ocean Class with a single tap — calm, quick, and kind."
        actions={
        <Button variant="emerald">
            <SaveIcon className="h-4 w-4" /> Save attendance
          </Button>
        } />
      

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Present"
          value={counts.present}
          icon="Check"
          tone="emerald" />
        
        <StatCard label="Late" value={counts.late} icon="Clock" tone="warm" />
        <StatCard label="Absent" value={counts.absent} icon="X" tone="rose" />
        <StatCard
          label="Excused"
          value={counts.excused}
          icon="ShieldCheck"
          tone="brand" />
        
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="overflow-hidden">
            <CardHeader
              title="Ocean Class · Today"
              subtitle="Tuesday, July 14 · 2026" />
            
            <div className="mt-3 divide-y divide-slate-100 dark:divide-slate-800">
              {roster.map((s) =>
              <div
                key={s.id}
                className="flex flex-col sm:flex-row sm:items-center gap-3 px-5 py-3">
                
                  <div className="flex items-center gap-3 flex-1">
                    <Avatar src={s.avatar} name={s.name} size={40} />
                    <div>
                      <p className="font-semibold text-sm text-slate-800 dark:text-slate-100">
                        {s.name}
                      </p>
                      <p className="text-xs text-slate-400">{s.admissionNo}</p>
                    </div>
                  </div>
                  <div className="flex gap-1.5">
                    {options.map((o) =>
                  <button
                    key={o.key}
                    onClick={() =>
                    setMarks((m) => ({
                      ...m,
                      [s.id]: o.key
                    }))
                    }
                    className={cn(
                      'inline-flex items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-xs font-semibold transition-colors',
                      marks[s.id] === o.key ?
                      o.active :
                      'bg-slate-100 dark:bg-slate-800 text-slate-500 hover:bg-slate-200/70 dark:hover:bg-slate-700'
                    )}>
                    
                        {o.icon}
                        <span className="hidden sm:inline">{o.label}</span>
                      </button>
                  )}
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader
              title="Monthly Trend"
              subtitle="Class attendance rate" />
            
            <div className="px-3 pb-4 pt-2">
              <AttendanceAreaChart height={200} />
            </div>
          </Card>
        </div>
      </div>
    </div>);

}