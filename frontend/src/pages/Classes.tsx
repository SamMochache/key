import React, { useEffect, useState } from 'react';
import { ArrowRightIcon, BookOpenIcon, UsersIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { cn } from '../lib/utils';
import { ApiClassroom, listClassrooms } from '../lib/api';

const accents = ['brand', 'emerald', 'warm'] as const;
const accent: Record<string, string> = {
  brand: 'bg-brand-600',
  emerald: 'bg-emerald-500',
  warm: 'bg-warm-500'
};

export function Classes() {
  const [classrooms, setClassrooms] = useState<ApiClassroom[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    listClassrooms({ active: true })
      .then((data) => mounted && setClassrooms(data))
      .catch((err) => mounted && setError(err instanceof Error ? err.message : 'Unable to load classes.'))
      .finally(() => mounted && setLoading(false));
    return () => { mounted = false; };
  }, []);

  return (
    <div>
      <PageHeader title="Classes" description="Our learning communities — each a prepared environment where children flourish together." />

      {loading && <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">{[1, 2, 3].map((item) => <Card key={item} className="h-56 animate-pulse bg-slate-100 dark:bg-slate-800/60" />)}</div>}

      {!loading && error && <Card className="p-6"><p className="text-sm font-semibold text-red-600 dark:text-red-400">Unable to load classes</p><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{error}</p></Card>}

      {!loading && !error && classrooms.length === 0 && <Card className="p-8 text-center"><p className="font-display font-bold text-slate-800 dark:text-slate-100">No active classes yet</p><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Create a classroom in the academic administration area to see it here.</p></Card>}

      {!loading && !error && classrooms.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {classrooms.map((classroom, index) => {
            const color = accents[index % accents.length];
            return (
              <Card key={classroom.id} className="overflow-hidden hover:-translate-y-1 transition-transform">
                <div className={cn('h-2', accent[color])} />
                <div className="p-5">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="font-display text-lg font-extrabold text-slate-900 dark:text-white">{classroom.name}</h3>
                    <Badge tone="slate">{classroom.stage_name}</Badge>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">{classroom.academic_year_name} · Term {classroom.term_number}</p>
                  <div className="grid grid-cols-3 gap-2 mt-5 text-center">
                    <Stat value={String(classroom.student_count)} label="Students" />
                    <Stat value={String(classroom.subject_count)} label="Subjects" />
                    <Stat value={`${classroom.capacity}`} label="Capacity" />
                  </div>
                  <div className="mt-5 flex items-center justify-between rounded-2xl bg-slate-50 dark:bg-slate-800/60 px-3.5 py-2.5">
                    <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400"><UsersIcon className="h-4 w-4" />{classroom.code}</div>
                    <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400"><BookOpenIcon className="h-4 w-4" />{classroom.subject_count} subjects</div>
                  </div>
                  <Link to={`/classes/${classroom.id}`} className="mt-5 w-full inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-100 dark:bg-slate-800 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-200/70 dark:hover:bg-slate-700 transition-colors">
                    Open class <ArrowRightIcon className="h-4 w-4" />
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 py-2.5"><p className="font-display font-extrabold text-slate-800 dark:text-slate-100">{value}</p><p className="text-[11px] text-slate-400 font-medium">{label}</p></div>;
}
