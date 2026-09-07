import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  GlobeIcon,
  CakeIcon,
  ArrowLeftIcon,
  SparklesIcon
} from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import { cn } from '../lib/utils';
import { getStudent, type ApiStudent } from '../lib/api';

const TABS = ['Overview', 'Attendance', 'Assessments', 'Assignments', 'Behaviour', 'Portfolio', 'Teacher Notes', 'AI Reports'];

export function StudentProfile() {
  const { id } = useParams();
  const [student, setStudent] = useState<ApiStudent | null>(null);
  const [tab, setTab] = useState('Overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);
    setError('');
    getStudent(id)
      .then((data) => {
        if (!cancelled) setStudent(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load student.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [id]);

  if (loading) return <Card className="p-8 text-center text-sm text-slate-500">Loading student…</Card>;
  if (!student) {
    return (
      <Card>
        <EmptyState
          icon="UserX"
          title="Student not found"
          description={error || 'This student is not available to your account.'}
          action={<Link to="/students"><Button>Back to students</Button></Link>}
        />
      </Card>
    );
  }

  const status = student.is_active ? 'Enrolled' : 'Pending';

  return (
    <div>
      <Link to="/students" className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-400 hover:text-brand-600 mb-4">
        <ArrowLeftIcon className="h-4 w-4" /> All students
      </Link>

      <Card className="p-6 mb-6">
        <div className="flex flex-col sm:flex-row gap-5">
          <Avatar name={student.full_name} size={88} className="ring-4 ring-brand-100 dark:ring-slate-800" />
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="font-display text-2xl font-extrabold text-slate-900 dark:text-white">{student.full_name}</h1>
              <Badge tone={status === 'Enrolled' ? 'emerald' : 'warm'}>{status}</Badge>
            </div>
            <p className="text-slate-400 mt-0.5">{student.admission_number} · {student.school_name}</p>
            <div className="flex flex-wrap gap-x-6 gap-y-2 mt-4 text-sm">
              <Meta icon={<CakeIcon className="h-4 w-4" />} label={`${student.date_of_birth} · Age ${student.age}`} />
              <Meta icon={<GlobeIcon className="h-4 w-4" />} label={student.nationality} />
            </div>
          </div>
          <div className="flex sm:flex-col gap-3">
            <Link to="/ai-reports"><Button className="w-full"><SparklesIcon className="h-4 w-4" /> AI Report</Button></Link>
            <Button variant="secondary">Message parent</Button>
          </div>
        </div>
      </Card>

      <div className="flex gap-1 overflow-x-auto mb-6 rounded-2xl bg-slate-100 dark:bg-slate-800/60 p-1">
        {TABS.map((t) => (
          <button key={t} onClick={() => setTab(t)} className={cn(
            'shrink-0 rounded-xl px-4 py-2 text-sm font-semibold transition-colors',
            tab === t ? 'bg-white dark:bg-slate-900 text-brand-600 shadow-soft' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
          )}>{t}</button>
        ))}
      </div>

      {tab === 'Overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader title="Student Information" subtitle="Current profile data" />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 px-5 pb-5 mt-2 text-sm">
                <Info label="Email" value={student.email} />
                <Info label="Gender" value={student.gender} />
                <Info label="Admission date" value={student.admission_date} />
                <Info label="Birth certificate" value={student.birth_certificate_number || 'Not provided'} />
              </div>
            </Card>
            <Card>
              <CardHeader title="Progress Timeline" />
              <EmptyState icon="Clock" title="No progress activity yet" description="Assessment, attendance, portfolio and teacher activity will appear here as those modules are connected." />
            </Card>
          </div>
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <StatBox label="Attendance" value="—" tone="text-emerald-600" />
              <StatBox label="Growth Index" value="—" tone="text-brand-600" />
            </div>
            <Card className="overflow-hidden">
              <CardHeader title="Latest Portfolio" />
              <EmptyState icon="Image" title="No portfolio entries yet" />
            </Card>
          </div>
        </div>
      )}

      {tab !== 'Overview' && (
        <Card>
          <EmptyState icon="FolderOpen" title={`${tab} — coming into view`} description={`This module will hold ${student.full_name.split(' ')[0]}’s ${tab.toLowerCase()} once its backend workflow is connected.`} />
        </Card>
      )}
    </div>
  );
}

function Meta({ icon, label }: { icon: React.ReactNode; label: string }) {
  return <span className="inline-flex items-center gap-2 text-slate-500 dark:text-slate-400"><span className="text-slate-300 dark:text-slate-600">{icon}</span>{label}</span>;
}

function Info({ label, value }: { label: string; value: string }) {
  return <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-4"><p className="text-xs font-semibold text-slate-400">{label}</p><p className="mt-1 text-slate-700 dark:text-slate-200 break-words">{value}</p></div>;
}

function StatBox({ label, value, tone }: { label: string; value: string; tone: string }) {
  return <Card className="p-4 text-center"><p className={cn('font-display text-2xl font-extrabold', tone)}>{value}</p><p className="text-xs text-slate-400 font-medium mt-0.5">{label}</p></Card>;
}
