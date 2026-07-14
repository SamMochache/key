import React from 'react';
import { Link } from 'react-router-dom';
import {
  CalendarCheckIcon,
  SparklesIcon,
  ClipboardCheckIcon,
  PlusIcon,
  ClockIcon,
  StickyNoteIcon } from
'lucide-react';
import { PageHeader } from '../ui/PageHeader';
import { StatCard } from '../ui/StatCard';
import { Card, CardHeader } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { ActivityFeed, MiniCalendar } from '../widgets/Widgets';
import { assignments } from '../../lib/data';
const todaysClasses = [
{
  time: '08:30',
  name: 'Ocean · Morning Work Cycle',
  room: 'Studio A',
  now: true
},
{
  time: '10:30',
  name: 'Language — Story Sequencing',
  room: 'Studio A',
  now: false
},
{
  time: '13:00',
  name: 'Culture — Leaf Study',
  room: 'Garden',
  now: false
},
{
  time: '14:30',
  name: 'Practical Life Observation',
  room: 'Studio A',
  now: false
}];

const quickActions = [
{
  label: 'Take Attendance',
  to: '/attendance',
  icon: CalendarCheckIcon,
  tone: 'bg-brand-600'
},
{
  label: 'Generate AI Report',
  to: '/ai-reports',
  icon: SparklesIcon,
  tone: 'bg-emerald-500'
},
{
  label: 'Grade Assignments',
  to: '/assessments',
  icon: ClipboardCheckIcon,
  tone: 'bg-warm-500'
}];

export function TeacherDashboard({ name }: {name: string;}) {
  return (
    <div>
      <PageHeader
        title={`Good morning, ${name.split(' ')[0]}`}
        description="Your Ocean Class is ready. Here’s what needs your attention today."
        actions={
        <Button>
            <PlusIcon className="h-4 w-4" /> New observation
          </Button>
        } />
      

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        {quickActions.map((a) =>
        <Link
          key={a.label}
          to={a.to}
          className="group flex items-center gap-3 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800 shadow-soft p-4 hover:-translate-y-0.5 transition-transform">
          
            <span
            className={`flex h-11 w-11 items-center justify-center rounded-2xl text-white ${a.tone}`}>
            
              <a.icon className="h-5 w-5" />
            </span>
            <span className="font-semibold text-slate-800 dark:text-slate-100">
              {a.label}
            </span>
          </Link>
        )}
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Today’s Classes"
          value={4}
          icon="CalendarDays"
          tone="brand" />
        
        <StatCard
          label="To Grade"
          value={12}
          icon="ClipboardList"
          tone="warm"
          hint="2 due today" />
        
        <StatCard
          label="Pending Reports"
          value={5}
          icon="Sparkles"
          tone="emerald" />
        
        <StatCard
          label="Class Attendance"
          value="95%"
          icon="CalendarCheck"
          tone="brand"
          delta={1} />
        
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader title="Today’s Schedule" subtitle="Tuesday, July 14" />
            <div className="px-3 pb-3 mt-2 space-y-1">
              {todaysClasses.map((c) =>
              <div
                key={c.time}
                className={`flex items-center gap-4 rounded-2xl px-3 py-3 ${c.now ? 'bg-brand-50 dark:bg-brand-600/15' : 'hover:bg-slate-50 dark:hover:bg-slate-800/60'}`}>
                
                  <span className="flex items-center gap-1.5 text-sm font-bold text-slate-700 dark:text-slate-200 w-16">
                    <ClockIcon className="h-4 w-4 text-slate-400" /> {c.time}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">
                      {c.name}
                    </p>
                    <p className="text-xs text-slate-400">{c.room}</p>
                  </div>
                  {c.now && <Badge tone="brand">Now</Badge>}
                </div>
              )}
            </div>
          </Card>

          <Card>
            <CardHeader
              title="Assignments to Grade"
              action={
              <Link
                to="/assessments"
                className="text-sm font-bold text-brand-600">
                
                  View all
                </Link>
              } />
            
            <div className="px-3 pb-3 mt-2 space-y-1">
              {assignments.map((a) =>
              <div
                key={a.id}
                className="flex items-center gap-3 rounded-2xl px-3 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/60">
                
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">
                      {a.title}
                    </p>
                    <p className="text-xs text-slate-400">
                      {a.subject} · {a.className} · Due {a.due}
                    </p>
                  </div>
                  <div className="hidden sm:flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-500">
                      {a.submitted}/{a.total}
                    </span>
                    <div className="w-20 h-1.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                      <div
                      className="h-full rounded-full bg-brand-500"
                      style={{
                        width: `${a.submitted / a.total * 100}%`
                      }} />
                    
                    </div>
                  </div>
                  <Badge tone={a.status === 'Grading' ? 'warm' : 'emerald'}>
                    {a.status}
                  </Badge>
                </div>
              )}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <MiniCalendar />
          <Card className="p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-display font-bold text-slate-800 dark:text-slate-100">
                Quick Notes
              </h3>
              <StickyNoteIcon className="h-5 w-5 text-slate-300" />
            </div>
            <textarea
              className="w-full h-28 resize-none rounded-2xl bg-warm-50 dark:bg-slate-800 border border-warm-100 dark:border-slate-700 p-3 text-sm text-slate-700 dark:text-slate-200 outline-none focus:ring-2 focus:ring-warm-500/40 placeholder:text-warm-600/50"
              placeholder="Noah showed great focus at the pink tower today…"
              defaultValue="Remember to prepare new threading works for Aria — she’s ready for the next challenge." />
            
          </Card>
          <ActivityFeed />
        </div>
      </div>
    </div>);

}