import React from 'react';
import { PageHeader } from '../ui/PageHeader';
import { StatCard } from '../ui/StatCard';
import { Card, CardHeader } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Avatar } from '../ui/Avatar';
import { ClassCompareBar, CompetencyRadarChart } from '../charts/Charts';
import { AnnouncementsCard, UpcomingEventsCard } from '../widgets/Widgets';
import { classes } from '../../lib/data';
export function PrincipalDashboard({ name }: {name: string;}) {
  return (
    <div>
      <PageHeader
        title={`Welcome, ${name.split(' ')[1] ?? name}`}
        description="A leadership view of school health — outcomes, wellbeing, and how each class is flourishing." />
      

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="School Growth Index"
          value="84"
          icon="TrendingUp"
          tone="emerald"
          delta={6} />
        
        <StatCard
          label="Avg Attendance"
          value="94%"
          icon="CalendarCheck"
          tone="brand"
          delta={2} />
        
        <StatCard
          label="Staff Wellbeing"
          value="Good"
          icon="HeartHandshake"
          tone="warm" />
        
        <StatCard
          label="Open Concerns"
          value={3}
          icon="AlertCircle"
          tone="rose"
          hint="Needs review" />
        
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader
              title="Class Comparison"
              subtitle="Growth vs attendance across classes" />
            
            <div className="px-3 pb-4 pt-2">
              <ClassCompareBar />
            </div>
          </Card>

          <Card>
            <CardHeader
              title="Class Health"
              subtitle="Each learning community at a glance" />
            
            <div className="px-3 pb-3 mt-2 space-y-1">
              {classes.map((c) =>
              <div
                key={c.id}
                className="flex items-center gap-3 rounded-2xl px-2 py-2.5 hover:bg-slate-50 dark:hover:bg-slate-800/60">
                
                  <Avatar src={c.teacherAvatar} name={c.teacher} size={38} />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm text-slate-800 dark:text-slate-100">
                      {c.name} Class
                    </p>
                    <p className="text-xs text-slate-400">
                      {c.teacher} · {c.ageGroup}
                    </p>
                  </div>
                  <div className="hidden sm:block w-28">
                    <div className="h-1.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                      <div
                      className="h-full rounded-full bg-emerald-500"
                      style={{
                        width: `${70 + c.students % 20}%`
                      }} />
                    
                    </div>
                  </div>
                  <Badge tone="emerald">{c.students} students</Badge>
                </div>
              )}
            </div>
          </Card>

          <AnnouncementsCard />
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader
              title="Competency Profile"
              subtitle="School-wide averages" />
            
            <div className="px-3 pb-4 pt-2">
              <CompetencyRadarChart />
            </div>
          </Card>
          <UpcomingEventsCard />
        </div>
      </div>
    </div>);

}