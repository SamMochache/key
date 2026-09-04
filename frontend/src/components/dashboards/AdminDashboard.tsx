import React from 'react';
import { UserPlusIcon, DownloadIcon } from 'lucide-react';
import { PageHeader } from '../ui/PageHeader';
import { StatCard } from '../ui/StatCard';
import { Card, CardHeader } from '../ui/Card';
import { Button } from '../ui/Button';
import { AttendanceAreaChart, GrowthLineChart } from '../charts/Charts';
import { AnnouncementsCard, UpcomingEventsCard, ActivityFeed, MiniCalendar } from '../widgets/Widgets';
import type { DashboardSummary } from '../../lib/api';

interface AdminDashboardProps {
  name: string;
  summary?: DashboardSummary | null;
}

export function AdminDashboard({ name, summary }: AdminDashboardProps) {
  const students = summary?.students ?? 214;
  const assessments = summary?.assessments ?? 24;
  const upcomingAssessments = summary?.upcoming_assessments ?? 17;

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
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Total Students"
          value={students}
          icon="Users"
          tone="brand"
          delta={4}
        />

        <StatCard
          label="Assessments"
          value={assessments}
          icon="ClipboardList"
          tone="emerald"
          hint={summary ? 'Live from API' : undefined}
        />

        <StatCard
          label="Upcoming Assessments"
          value={upcomingAssessments}
          icon="CalendarDays"
          tone="warm"
          hint="Based on due date"
        />

        <StatCard
          label="Evaluation Progress"
          value={summary ? `${summary.evaluations ? Math.round((summary.published_evaluations / summary.evaluations) * 100) : 0}%` : '96%'}
          icon="Award"
          tone="brand"
          hint={summary ? `${summary.published_evaluations}/${summary.evaluations} published` : undefined}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader
              title="Attendance Trend"
              subtitle="School-wide, last 6 months"
              action={<span className="text-sm font-bold text-emerald-600">+3% vs last term</span>}
            />
            <div className="px-3 pb-4 pt-2">
              <AttendanceAreaChart />
            </div>
          </Card>

          <Card>
            <CardHeader title="Student Growth Overview" subtitle="Average competency by learning area" />
            <div className="px-3 pb-4 pt-2">
              <GrowthLineChart />
            </div>
          </Card>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <StatCard
              label="Assessment Submissions"
              value={summary?.submissions ?? 56}
              icon="ClipboardCheck"
              tone="warm"
              hint={summary ? 'Live from API' : 'Prototype data'}
            />
            <StatCard label="Upcoming Events" value={5} icon="CalendarDays" tone="brand" hint="Next 10 days" />
          </div>

          <AnnouncementsCard />
        </div>

        <div className="space-y-6">
          <MiniCalendar />
          <UpcomingEventsCard />
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}
