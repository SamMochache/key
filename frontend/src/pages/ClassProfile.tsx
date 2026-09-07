import React, { useEffect, useState } from 'react';
import { ArrowLeftIcon, BookOpenIcon, GraduationCapIcon, UsersIcon } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Card, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import { cn } from '../lib/utils';
import { getClassroom, listEnrollments, listStageSubjects, type ApiClassroom, type ApiEnrollment, type ApiStageSubject } from '../lib/api';

export function ClassProfile() {
  const { id } = useParams();
  const [classroom, setClassroom] = useState<ApiClassroom | null>(null);
  const [enrollments, setEnrollments] = useState<ApiEnrollment[]>([]);
  const [subjects, setSubjects] = useState<ApiStageSubject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);
    Promise.all([
      getClassroom(id),
      listEnrollments({ classroom: id, status: 'ENROLLED' }),
    ])
      .then(async ([classData, enrollmentData]) => {
        const subjectData = classData.cambridge_stage
          ? await listStageSubjects({ stage: classData.cambridge_stage, active: true })
          : [];
        if (!cancelled) {
          setClassroom(classData);
          setEnrollments(enrollmentData);
          setSubjects(subjectData);
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load class.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [id]);

  if (loading) return <Card className="p-8 text-center text-sm text-slate-500">Loading class…</Card>;
  if (!classroom) {
    return (
      <Card>
        <EmptyState icon="School" title="Class not found" description={error || 'This class is not available to your account.'} action={<Link to="/classes"><Button>Back to classes</Button></Link>} />
      </Card>
    );
  }

  const occupancy = classroom.capacity ? Math.round((classroom.student_count / classroom.capacity) * 100) : 0;

  return (
    <div>
      <Link to="/classes" className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-400 hover:text-brand-600 mb-4">
        <ArrowLeftIcon className="h-4 w-4" /> All classes
      </Link>

      <PageHeader
        title={classroom.name}
        description={`${classroom.stage_name} · ${classroom.academic_year_name} · Term ${classroom.term_number}`}
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatBox label="Students" value={classroom.student_count} icon={<UsersIcon className="h-4 w-4" />} />
        <StatBox label="Capacity" value={classroom.capacity} icon={<GraduationCapIcon className="h-4 w-4" />} />
        <StatBox label="Subjects" value={subjects.length} icon={<BookOpenIcon className="h-4 w-4" />} />
        <StatBox label="Occupancy" value={`${occupancy}%`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader title="Enrolled Students" subtitle={`${enrollments.length} active students in this class`} />
          <div className="px-5 pb-5 mt-3">
            {enrollments.length === 0 ? (
              <EmptyState icon="Users" title="No enrolled students" description="Students will appear here once they are enrolled in this classroom." />
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {enrollments.map((enrollment) => (
                  <Link key={enrollment.id} to={`/students/${enrollment.student}`} className="flex items-center gap-3 py-3 first:pt-1 hover:bg-slate-50 dark:hover:bg-slate-800/40 rounded-xl px-2 transition-colors">
                    <Avatar name={enrollment.student_name} size={40} />
                    <div className="min-w-0 flex-1">
                      <p className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">{enrollment.student_name}</p>
                      <p className="text-xs text-slate-400">{enrollment.admission_number} · Enrolled {enrollment.enrollment_date}</p>
                    </div>
                    <Badge tone="emerald">Enrolled</Badge>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </Card>

        <Card>
          <CardHeader title="Subjects" subtitle="Active stage subjects" />
          <div className="px-5 pb-5 mt-3 space-y-2">
            {subjects.length === 0 ? (
              <EmptyState icon="BookOpen" title="No subjects assigned" />
            ) : subjects.map((subject) => (
              <div key={subject.id} className="flex items-center justify-between gap-3 rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-3">
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">{subject.subject_name}</p>
                  <p className="text-xs text-slate-400">{subject.weekly_lessons} lessons/week</p>
                </div>
                <Badge tone={subject.is_core ? 'emerald' : 'slate'}>{subject.is_core ? 'Core' : 'Elective'}</Badge>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function StatBox({ label, value, icon }: { label: string; value: string | number; icon?: React.ReactNode }) {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-center gap-1.5 text-slate-400 text-xs font-semibold">{icon}{label}</div>
      <p className={cn('font-display text-2xl font-extrabold text-center mt-1 text-slate-800 dark:text-slate-100')}>{value}</p>
    </Card>
  );
}
