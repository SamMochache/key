import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CalendarDaysIcon, DownloadIcon, Loader2Icon, UserPlusIcon } from 'lucide-react';
import { PageHeader } from '../ui/PageHeader';
import { StatCard } from '../ui/StatCard';
import { Card, CardHeader } from '../ui/Card';
import { AttendanceAreaChart, GrowthLineChart } from '../charts/Charts';
import { useApp } from '../../context/AppContext';
import { getAnalytics, listAssessments, listClassrooms, listTeachers, type AnalyticsData } from '../../lib/api';
import { listCalendarEvents, type ApiCalendarEvent } from '../../lib/calendarApi';

export function AdminDashboard({ name }: { name: string }) {
  const { school } = useApp();
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [teacherCount, setTeacherCount] = useState<number | null>(null);
  const [classCount, setClassCount] = useState<number | null>(null);
  const [assessmentCount, setAssessmentCount] = useState<number | null>(null);
  const [events, setEvents] = useState<ApiCalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    setError('');
    Promise.all([
      getAnalytics(),
      listTeachers(),
      listClassrooms({ active: true }),
      listAssessments(),
      listCalendarEvents(),
    ])
      .then(([analyticsData, teachers, classrooms, assessments, calendarEvents]) => {
        setAnalytics(analyticsData);
        setTeacherCount(teachers.length);
        setClassCount(classrooms.length);
        setAssessmentCount(assessments.filter(item => item.status !== 'GRADED').length);
        setEvents(calendarEvents
          .filter(item => new Date(item.end_at).getTime() >= Date.now())
          .sort((a, b) => new Date(a.start_at).getTime() - new Date(b.start_at).getTime())
          .slice(0, 6));
      })
      .catch(err => setError(err instanceof Error ? err.message : 'Unable to load dashboard data.'))
      .finally(() => setLoading(false));
  }, []);

  const schoolName = school?.name || 'KEY platform';
  const summary = analytics?.summary;

  return (
    <div>
      <PageHeader
        title={`Good morning, ${name.split(' ')[0]}`}
        description={`Live operational overview for ${schoolName}.`}
        actions={
          <>
            <Link to="/reports" className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
              <DownloadIcon className="h-4 w-4" /> Reports
            </Link>
            <Link to="/students" className="inline-flex items-center gap-2 rounded-2xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700">
              <UserPlusIcon className="h-4 w-4" /> Enroll student
            </Link>
          </>
        }
      />

      {error && <div role="alert" className="mb-5 rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700 dark:bg-rose-500/10 dark:text-rose-300">{error}</div>}
      {loading && <div className="mb-5 flex items-center gap-2 text-sm text-slate-400"><Loader2Icon className="h-4 w-4 animate-spin" /> Loading live dashboard data…</div>}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Students" value={summary?.students ?? '—'} icon="Users" tone="brand" />
        <StatCard label="Teachers" value={teacherCount ?? '—'} icon="GraduationCap" tone="emerald" />
        <StatCard label="Classes" value={classCount ?? '—'} icon="School" tone="warm" />
        <StatCard label="Attendance" value={summary?.attendance_rate == null ? '—' : `${summary.attendance_rate}%`} icon="CalendarCheck" tone="brand" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader title="Attendance Trend" subtitle="Recorded attendance over the last six months" />
            <div className="px-3 pb-4 pt-2">
              {analytics?.attendance_trend?.length ? <AttendanceAreaChart data={analytics.attendance_trend} /> : <EmptyState text="No attendance records yet." />}
            </div>
          </Card>

          <Card>
            <CardHeader title="Student Growth Overview" subtitle="Published assessment performance by term" />
            <div className="px-3 pb-4 pt-2">
              {analytics?.growth_trend?.length ? <GrowthLineChart data={analytics.growth_trend} /> : <EmptyState text="No published evaluation trend yet." />}
            </div>
          </Card>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <StatCard label="Open Assessments" value={assessmentCount ?? '—'} icon="ClipboardList" tone="warm" />
            <StatCard label="Upcoming Events" value={events.length} icon="CalendarDays" tone="brand" />
          </div>
        </div>

        <Card>
          <CardHeader title="Upcoming Events" subtitle="Live institution calendar" action={<CalendarDaysIcon className="h-5 w-5 text-slate-300" />} />
          <div className="px-4 pb-4 space-y-2">
            {events.length === 0 ? <EmptyState text="No upcoming events." /> : events.map(event => (
              <div key={event.id} className="rounded-2xl border border-slate-100 px-3 py-3 dark:border-slate-800">
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{event.title}</p>
                <p className="mt-1 text-xs text-slate-400">{new Date(event.start_at).toLocaleString()} {event.location ? `· ${event.location}` : ''}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return <div className="flex min-h-28 items-center justify-center px-4 text-center text-sm text-slate-400">{text}</div>;
}
