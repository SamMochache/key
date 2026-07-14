import React from 'react';
import { UserPlusIcon, DownloadIcon } from 'lucide-react';
import { PageHeader } from '../ui/PageHeader';
import { StatCard } from '../ui/StatCard';
import { Card, CardHeader } from '../ui/Card';
import { Button } from '../ui/Button';
import { AttendanceAreaChart, GrowthLineChart } from '../charts/Charts';
import {
  AnnouncementsCard,
  UpcomingEventsCard,
  ActivityFeed,
  MiniCalendar } from
'../widgets/Widgets';
export function AdminDashboard({ name }: {name: string;}) {
  return (
    <div>
      <PageHeader
        title={`Good morning, ${name.split(' ')[0]}`}
        description="Here’s how Key International School is growing today — a calm overview of your whole community."
        actions={
        <>
            <Button variant="secondary">
              <DownloadIcon className="h-4 w-4" /> Export
            </Button>
            <Button>
              <UserPlusIcon className="h-4 w-4" /> Enroll student
            </Button>
          </>
        } />
      

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Total Students"
          value={214}
          icon="Users"
          tone="brand"
          delta={4} />
        
        <StatCard
          label="Teachers"
          value={28}
          icon="GraduationCap"
          tone="emerald"
          delta={2} />
        
        <StatCard
          label="Classes"
          value={12}
          icon="School"
          tone="warm"
          hint="Across 4 streams" />
        
        <StatCard
          label="Attendance Today"
          value="96%"
          icon="CalendarCheck"
          tone="brand"
          delta={1} />
        
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader
              title="Attendance Trend"
              subtitle="School-wide, last 6 months"
              action={
              <span className="text-sm font-bold text-emerald-600">
                  +3% vs last term
                </span>
              } />
            
            <div className="px-3 pb-4 pt-2">
              <AttendanceAreaChart />
            </div>
          </Card>

          <Card>
            <CardHeader
              title="Student Growth Overview"
              subtitle="Average competency by learning area" />
            
            <div className="px-3 pb-4 pt-2">
              <GrowthLineChart />
            </div>
          </Card>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <StatCard
              label="Assignments Due"
              value={17}
              icon="ClipboardList"
              tone="warm"
              hint="This week" />
            
            <StatCard
              label="Upcoming Events"
              value={5}
              icon="CalendarDays"
              tone="brand"
              hint="Next 10 days" />
            
          </div>

          <AnnouncementsCard />
        </div>

        <div className="space-y-6">
          <MiniCalendar />
          <UpcomingEventsCard />
          <ActivityFeed />
        </div>
      </div>
    </div>);

}