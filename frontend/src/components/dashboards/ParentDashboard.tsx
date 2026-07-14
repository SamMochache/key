import React from 'react';
import { Link } from 'react-router-dom';
import {
  MessageSquareIcon,
  SparklesIcon,
  BookOpenIcon,
  CalendarCheckIcon,
  ArrowRightIcon } from
'lucide-react';
import { PageHeader } from '../ui/PageHeader';
import { Card, CardHeader } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Avatar } from '../ui/Avatar';
import { GrowthLineChart } from '../charts/Charts';
import { UpcomingEventsCard, AnnouncementsCard } from '../widgets/Widgets';
import { students, assignments, PORTFOLIO_IMG } from '../../lib/data';
export function ParentDashboard({ name }: {name: string;}) {
  const child = students[0];
  return (
    <div>
      <PageHeader
        title="Your family dashboard"
        description={`A warm window into ${child.name.split(' ')[0]}’s days at Key International School.`}
        actions={
        <Link to="/communication">
            <span className="inline-flex items-center gap-2 rounded-2xl bg-brand-600 text-white px-4 py-2.5 text-sm font-semibold hover:bg-brand-700">
              <MessageSquareIcon className="h-4 w-4" /> Message guide
            </span>
          </Link>
        } />
      

      <Card className="p-5 mb-6 overflow-hidden">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5">
          <Avatar
            src={child.avatar}
            name={child.name}
            size={72}
            ring
            className="ring-4 ring-brand-100 dark:ring-slate-800" />
          
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="font-display text-xl font-extrabold text-slate-900 dark:text-white">
                {child.name}
              </h2>
              <Badge tone="brand">{child.className} Class</Badge>
              <Badge tone="emerald">Enrolled</Badge>
            </div>
            <p className="text-sm text-slate-400 mt-0.5">
              Age {child.age} · {child.stream} · House {child.house}
            </p>
          </div>
          <div className="flex gap-6">
            <div className="text-center">
              <p className="font-display text-2xl font-extrabold text-emerald-600">
                {child.attendance}%
              </p>
              <p className="text-xs text-slate-400 font-medium">Attendance</p>
            </div>
            <div className="text-center">
              <p className="font-display text-2xl font-extrabold text-brand-600">
                {child.growth}
              </p>
              <p className="text-xs text-slate-400 font-medium">Growth Index</p>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader
              title="Progress this year"
              subtitle="How Mia is flourishing across learning areas"
              action={
              <Link
                to="/ai-reports"
                className="text-sm font-bold text-brand-600 inline-flex items-center gap-1">
                
                  Full report <ArrowRightIcon className="h-3.5 w-3.5" />
                </Link>
              } />
            
            <div className="px-3 pb-4 pt-2">
              <GrowthLineChart />
            </div>
          </Card>

          <Card>
            <CardHeader
              title="Homework & Assignments"
              action={
              <Link
                to="/assessments"
                className="text-sm font-bold text-brand-600">
                
                  View all
                </Link>
              } />
            
            <div className="px-3 pb-3 mt-2 space-y-1">
              {assignments.slice(0, 3).map((a) =>
              <div
                key={a.id}
                className="flex items-center gap-3 rounded-2xl px-3 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/60">
                
                  <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-50 dark:bg-slate-800 text-brand-600">
                    <BookOpenIcon className="h-4 w-4" />
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">
                      {a.title}
                    </p>
                    <p className="text-xs text-slate-400">
                      {a.subject} · Due {a.due}
                    </p>
                  </div>
                  <Badge tone={a.status === 'Grading' ? 'emerald' : 'warm'}>
                    {a.status === 'Grading' ? 'Submitted' : 'To do'}
                  </Badge>
                </div>
              )}
            </div>
          </Card>

          <Card>
            <CardHeader
              title="Teacher Comment"
              subtitle="From Sophie Laurent · 2 days ago"
              action={<SparklesIcon className="h-5 w-5 text-emerald-500" />} />
            
            <div className="px-5 pb-5 mt-1">
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                “Mia has been wonderfully absorbed in her leaf study this week,
                showing real patience and care. She’s beginning to guide younger
                friends — a lovely sign of growing leadership.”
              </p>
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="overflow-hidden">
            <CardHeader
              title="Latest Portfolio"
              action={
              <Link
                to="/portfolio"
                className="text-sm font-bold text-brand-600">
                
                  Open
                </Link>
              } />
            
            <div className="p-4 pt-3">
              <img
                src={PORTFOLIO_IMG}
                alt="Mia's latest artwork"
                className="w-full h-40 object-cover rounded-2xl" />
              
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100 mt-3">
                Autumn Leaf Collage
              </p>
              <p className="text-xs text-slate-400">Added by Sophie · Jul 12</p>
            </div>
          </Card>
          <UpcomingEventsCard />
          <AnnouncementsCard />
        </div>
      </div>
    </div>);

}