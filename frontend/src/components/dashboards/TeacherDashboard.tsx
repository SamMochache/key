import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { CalendarCheckIcon, ClipboardCheckIcon, ClockIcon, PlusIcon, SparklesIcon } from 'lucide-react';
import { PageHeader } from '../ui/PageHeader';
import { StatCard } from '../ui/StatCard';
import { Card, CardHeader } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useApp } from '../../context/AppContext';
import { getAnalytics, listAssessments, type AnalyticsData, type ApiAssessment } from '../../lib/api';
import { listTeacherSubjects, listTimetableEntries, type ApiTimetableEntry, type ApiTeacherSubject, type WeekDay } from '../../lib/timetableApi';
import { listCalendarEvents, type ApiCalendarEvent } from '../../lib/calendarApi';

const quickActions = [
  { label: 'Take Attendance', to: '/attendance', icon: CalendarCheckIcon, tone: 'bg-brand-600' },
  { label: 'Generate AI Report', to: '/ai-reports', icon: SparklesIcon, tone: 'bg-emerald-500' },
  { label: 'Assess & Grade', to: '/assessments', icon: ClipboardCheckIcon, tone: 'bg-warm-500' },
];

const weekday: WeekDay[] = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'];

export function TeacherDashboard({ name }: { name: string }) {
  const { school } = useApp();
  const [assignments, setAssignments] = useState<ApiTeacherSubject[]>([]);
  const [entries, setEntries] = useState<ApiTimetableEntry[]>([]);
  const [assessments, setAssessments] = useState<ApiAssessment[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [events, setEvents] = useState<ApiCalendarEvent[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    setError('');
    Promise.all([
      listTeacherSubjects({ active: true }),
      listTimetableEntries({ published: true }),
      listAssessments(),
      getAnalytics(),
      listCalendarEvents(),
    ]).then(([teacherAssignments, timetableEntries, assessmentRows, analyticsData, calendarEvents]) => {
      setAssignments(teacherAssignments);
      const assignmentIds = new Set(teacherAssignments.map(item => item.id));
      setEntries(timetableEntries.filter(item => assignmentIds.has(item.teacher_subject)));
      setAssessments(assessmentRows);
      setAnalytics(analyticsData);
      setEvents(calendarEvents.filter(item => new Date(item.end_at).getTime() >= Date.now()).slice(0, 5));
    }).catch(err => setError(err instanceof Error ? err.message : 'Unable to load teacher dashboard.'));
  }, []);

  const todayCode = weekday[new Date().getDay() - 1];
  const todaysClasses = useMemo(
    () => entries.filter(item => item.weekday === todayCode).sort((a, b) => a.start_time.localeCompare(b.start_time)),
    [entries, todayCode],
  );
  const activeAssessments = assessments.filter(item => item.status === 'PUBLISHED' || item.status === 'DRAFT');
  const schoolName = school?.name || 'your institution';

  return (
    <div>
      <PageHeader
        title={`Good morning, ${name.split(' ')[0]}`}
        description={`${schoolName} is ready. This dashboard is built from your current assignments and records.`}
        actions={<Link to="/evidence" className="inline-flex items-center gap-2 rounded-2xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700"><PlusIcon className="h-4 w-4" /> New evidence</Link>}
      />

      {error && <div role="alert" className="mb-5 rounded-2xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700 dark:bg-rose-500/10 dark:text-rose-300">{error}</div>}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        {quickActions.map(action => (
          <Link key={action.label} to={action.to} className="group flex items-center gap-3 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200/70 dark:border-slate-800 shadow-soft p-4 hover:-translate-y-0.5 transition-transform">
            <span className={`flex h-11 w-11 items-center justify-center rounded-2xl text-white ${action.tone}`}><action.icon className="h-5 w-5" /></span>
            <span className="font-semibold text-slate-800 dark:text-slate-100">{action.label}</span>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Today’s Classes" value={todaysClasses.length} icon="CalendarDays" tone="brand" />
        <StatCard label="Assigned Subjects" value={assignments.length} icon="BookOpen" tone="emerald" />
        <StatCard label="Active Assessments" value={activeAssessments.length} icon="ClipboardList" tone="warm" />
        <StatCard label="Recorded Attendance" value={analytics?.summary.attendance_rate == null ? '—' : `${analytics.summary.attendance_rate}%`} icon="CalendarCheck" tone="brand" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader title="Today’s Schedule" subtitle={new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })} />
            <div className="px-3 pb-3 mt-2 space-y-1">
              {todaysClasses.length === 0 ? <Empty text="No assigned timetable entries today." /> : todaysClasses.map(item => (
                <div key={item.id} className="flex items-center gap-4 rounded-2xl px-3 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/60">
                  <span className="flex items-center gap-1.5 text-sm font-bold text-slate-700 dark:text-slate-200 w-20"><ClockIcon className="h-4 w-4 text-slate-400" /> {item.start_time.slice(0, 5)}</span>
                  <div className="flex-1 min-w-0"><p className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">{item.subject_name} · {item.classroom_name}</p><p className="text-xs text-slate-400">{item.room || item.period_name}</p></div>
                  <Badge tone="brand">{item.period_name}</Badge>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <CardHeader title="Assessments" action={<Link to="/assessments" className="text-sm font-bold text-brand-600">View all</Link>} />
            <div className="px-3 pb-3 mt-2 space-y-1">
              {activeAssessments.length === 0 ? <Empty text="No active assessments." /> : activeAssessments.slice(0, 6).map(item => (
                <div key={item.id} className="flex items-center gap-3 rounded-2xl px-3 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/60">
                  <div className="flex-1 min-w-0"><p className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">{item.title}</p><p className="text-xs text-slate-400">{item.assessment_type}{item.due_date ? ` · Due ${new Date(item.due_date).toLocaleDateString()}` : ''}</p></div>
                  <Badge tone={item.status === 'PUBLISHED' ? 'emerald' : 'warm'}>{item.status}</Badge>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <Card>
          <CardHeader title="Upcoming Events" subtitle="Institution calendar" />
          <div className="px-4 pb-4 space-y-2">
            {events.length === 0 ? <Empty text="No upcoming events." /> : events.map(event => (
              <div key={event.id} className="rounded-2xl border border-slate-100 px-3 py-3 dark:border-slate-800"><p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{event.title}</p><p className="mt-1 text-xs text-slate-400">{new Date(event.start_at).toLocaleString()}</p></div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function Empty({ text }: { text: string }) {
  return <div className="px-4 py-8 text-center text-sm text-slate-400">{text}</div>;
}
