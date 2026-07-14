import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  PhoneIcon,
  HeartPulseIcon,
  GlobeIcon,
  LanguagesIcon,
  CakeIcon,
  ArrowLeftIcon,
  SparklesIcon } from
'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import {
  GrowthLineChart,
  AttendanceAreaChart } from
'../components/charts/Charts';
import { students, PORTFOLIO_IMG } from '../lib/data';
import { cn } from '../lib/utils';
const TABS = [
'Overview',
'Attendance',
'Assessments',
'Assignments',
'Behaviour',
'Portfolio',
'Teacher Notes',
'AI Reports'];

const timeline = [
{
  date: 'Jul 12',
  text: 'Completed autumn leaf collage — deep focus observed.',
  tone: 'emerald'
},
{
  date: 'Jul 08',
  text: 'Began independent reading of first storybook.',
  tone: 'brand'
},
{
  date: 'Jul 02',
  text: 'Helped a younger friend with pouring work.',
  tone: 'warm'
},
{
  date: 'Jun 24',
  text: 'Mastered golden bead addition to 100.',
  tone: 'brand'
}];

export function StudentProfile() {
  const { id } = useParams();
  const student = students.find((s) => s.id === id);
  const [tab, setTab] = useState('Overview');
  if (!student) {
    return (
      <Card>
        <EmptyState
          icon="UserX"
          title="Student not found"
          action={
          <Link to="/students">
              <Button>Back to students</Button>
            </Link>
          } />
        
      </Card>);

  }
  return (
    <div>
      <Link
        to="/students"
        className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-400 hover:text-brand-600 mb-4">
        
        <ArrowLeftIcon className="h-4 w-4" /> All students
      </Link>

      <Card className="p-6 mb-6">
        <div className="flex flex-col sm:flex-row gap-5">
          <Avatar
            src={student.avatar}
            name={student.name}
            size={88}
            className="ring-4 ring-brand-100 dark:ring-slate-800" />
          
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="font-display text-2xl font-extrabold text-slate-900 dark:text-white">
                {student.name}
              </h1>
              <Badge tone="emerald">{student.status}</Badge>
            </div>
            <p className="text-slate-400 mt-0.5">
              {student.admissionNo} · {student.className} Class ·{' '}
              {student.stream}
            </p>
            <div className="flex flex-wrap gap-x-6 gap-y-2 mt-4 text-sm">
              <Meta
                icon={<CakeIcon className="h-4 w-4" />}
                label={`${student.dob} · Age ${student.age}`} />
              
              <Meta
                icon={<GlobeIcon className="h-4 w-4" />}
                label={student.nationality} />
              
              <Meta
                icon={<LanguagesIcon className="h-4 w-4" />}
                label={student.languages.join(', ')} />
              
              <Meta
                icon={<PhoneIcon className="h-4 w-4" />}
                label={`${student.parent} · ${student.parentPhone}`} />
              
              <Meta
                icon={<HeartPulseIcon className="h-4 w-4" />}
                label={student.medicalNotes} />
              
            </div>
          </div>
          <div className="flex sm:flex-col gap-3">
            <Link to="/ai-reports">
              <Button className="w-full">
                <SparklesIcon className="h-4 w-4" /> AI Report
              </Button>
            </Link>
            <Button variant="secondary">Message parent</Button>
          </div>
        </div>
      </Card>

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto mb-6 rounded-2xl bg-slate-100 dark:bg-slate-800/60 p-1">
        {TABS.map((t) =>
        <button
          key={t}
          onClick={() => setTab(t)}
          className={cn(
            'shrink-0 rounded-xl px-4 py-2 text-sm font-semibold transition-colors',
            tab === t ?
            'bg-white dark:bg-slate-900 text-brand-600 shadow-soft' :
            'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
          )}>
          
            {t}
          </button>
        )}
      </div>

      {tab === 'Overview' &&
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader
              title="Growth by Learning Area"
              subtitle="Across the year" />
            
              <div className="px-3 pb-4 pt-2">
                <GrowthLineChart />
              </div>
            </Card>
            <Card>
              <CardHeader title="Progress Timeline" />
              <div className="px-5 pb-5 mt-2 space-y-4">
                {timeline.map((t, i) =>
              <div key={i} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <span
                    className={cn(
                      'h-3 w-3 rounded-full mt-1',
                      t.tone === 'emerald' && 'bg-emerald-500',
                      t.tone === 'brand' && 'bg-brand-500',
                      t.tone === 'warm' && 'bg-warm-500'
                    )} />
                  
                      {i < timeline.length - 1 &&
                  <span className="w-px flex-1 bg-slate-100 dark:bg-slate-800 mt-1" />
                  }
                    </div>
                    <div className="pb-1">
                      <p className="text-xs font-semibold text-slate-400">
                        {t.date}
                      </p>
                      <p className="text-sm text-slate-700 dark:text-slate-200">
                        {t.text}
                      </p>
                    </div>
                  </div>
              )}
              </div>
            </Card>
          </div>
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <StatBox
              label="Attendance"
              value={`${student.attendance}%`}
              tone="text-emerald-600" />
            
              <StatBox
              label="Growth Index"
              value={String(student.growth)}
              tone="text-brand-600" />
            
            </div>
            <Card className="overflow-hidden">
              <CardHeader title="Latest Portfolio" />
              <div className="p-4 pt-3">
                <img
                src={PORTFOLIO_IMG}
                alt="Portfolio"
                className="w-full h-40 object-cover rounded-2xl" />
              
              </div>
            </Card>
          </div>
        </div>
      }

      {tab === 'Attendance' &&
      <Card>
          <CardHeader
          title="Attendance History"
          subtitle="Monthly presence rate" />
        
          <div className="px-3 pb-4 pt-2">
            <AttendanceAreaChart height={280} />
          </div>
        </Card>
      }

      {tab !== 'Overview' && tab !== 'Attendance' &&
      <Card>
          <EmptyState
          icon="FolderOpen"
          title={`${tab} — coming into view`}
          description={`This tab will hold ${student.name.split(' ')[0]}’s ${tab.toLowerCase()}. Deep module in progress.`} />
        
        </Card>
      }
    </div>);

}
function Meta({ icon, label }: {icon: React.ReactNode;label: string;}) {
  return (
    <span className="inline-flex items-center gap-2 text-slate-500 dark:text-slate-400">
      <span className="text-slate-300 dark:text-slate-600">{icon}</span>
      {label}
    </span>);

}
function StatBox({
  label,
  value,
  tone




}: {label: string;value: string;tone: string;}) {
  return (
    <Card className="p-4 text-center">
      <p className={cn('font-display text-2xl font-extrabold', tone)}>
        {value}
      </p>
      <p className="text-xs text-slate-400 font-medium mt-0.5">{label}</p>
    </Card>);

}