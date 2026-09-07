import React, { useEffect, useState } from 'react';
import * as Icons from 'lucide-react';
import { EyeIcon, TargetIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { ApiAcademicYear, ApiSubject, ApiTerm, listAcademicYears, listSubjects, listTerms } from '../lib/api';
import { cn } from '../lib/utils';

const tone: Record<string, string> = {
  brand: 'bg-brand-50 text-brand-600 dark:bg-brand-600/20 dark:text-brand-300',
  emerald: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-300',
  warm: 'bg-warm-50 text-warm-600 dark:bg-warm-500/20 dark:text-warm-300'
};
const tones = ['emerald', 'warm', 'brand', 'brand', 'emerald', 'warm'];

const learningGoals = [
  'Develops concentration through the full work cycle',
  'Builds independence and care for the environment',
  'Grows language through phonetic and expressive work',
  'Explores mathematics with concrete materials'
];

export function Academics() {
  const [subjects, setSubjects] = useState<ApiSubject[]>([]);
  const [academicYears, setAcademicYears] = useState<ApiAcademicYear[]>([]);
  const [terms, setTerms] = useState<ApiTerm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    Promise.all([
      listSubjects({ active: true }),
      listAcademicYears({ current: true }),
    ])
      .then(([subjectData, yearData]) => {
        if (!mounted) return;
        setSubjects(subjectData);
        setAcademicYears(yearData);
        if (yearData[0]) {
          return listTerms({ academicYear: yearData[0].id });
        }
        return [];
      })
      .then((termData) => mounted && setTerms(termData as ApiTerm[]))
      .catch((err) => mounted && setError(err instanceof Error ? err.message : 'Unable to load academic data.'))
      .finally(() => mounted && setLoading(false));
    return () => { mounted = false; };
  }, []);

  const currentYear = academicYears.find((year) => year.is_current) ?? academicYears[0];
  const currentTerm = terms.find((term) => term.is_current) ?? terms[0];

  return (
    <div>
      <PageHeader
        title="Academics"
        description="Montessori learning areas, lessons, and the academic structure guiding each child’s path."
      />

      {error && (
        <Card className="p-5 mb-6">
          <p className="text-sm font-semibold text-red-600 dark:text-red-400">Unable to load academic data</p>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{error}</p>
        </Card>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {loading && [1, 2, 3].map((item) => (
          <Card key={item} className="h-24 animate-pulse bg-slate-100 dark:bg-slate-800/60" />
        ))}
        {!loading && subjects.map((subject, index) => {
          const Icon = (Icons as any)[index % 2 === 0 ? 'BookOpen' : 'Shapes'] ?? Icons.BookOpen;
          const subjectTone = tones[index % tones.length];
          return (
            <Card key={subject.id} className="p-5 hover:-translate-y-0.5 transition-transform">
              <div className="flex items-center gap-3">
                <span className={cn('flex h-12 w-12 items-center justify-center rounded-2xl', tone[subjectTone])}>
                  <Icon className="h-5 w-5" />
                </span>
                <div className="min-w-0">
                  <h3 className="font-display font-bold text-slate-800 dark:text-slate-100 truncate">
                    {subject.name}
                  </h3>
                  <p className="text-xs text-slate-400">
                    {subject.code} · {subject.is_core ? 'core' : 'elective'} · continuous assessment
                  </p>
                </div>
              </div>
            </Card>
          );
        })}
        {!loading && !error && subjects.length === 0 && (
          <Card className="p-6 sm:col-span-2 lg:col-span-3 text-center">
            <p className="font-semibold text-slate-800 dark:text-slate-100">No active subjects configured</p>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Add subjects to the curriculum to populate this area.</p>
          </Card>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader
            title="Current Academic Period"
            action={<TargetIcon className="h-5 w-5 text-emerald-500" />}
          />
          <div className="px-5 pb-5 mt-2 space-y-3">
            <PeriodRow label="Academic year" value={currentYear?.name ?? 'Not configured'} />
            <PeriodRow label="Current term" value={currentTerm ? `Term ${currentTerm.term_number}` : 'Not configured'} />
            {currentTerm && <PeriodRow label="Term dates" value={`${formatDate(currentTerm.start_date)} – ${formatDate(currentTerm.end_date)}`} />}
            {currentYear && <PeriodRow label="School year" value={`${formatDate(currentYear.start_date)} – ${formatDate(currentYear.end_date)}`} />}
          </div>
        </Card>

        <Card>
          <CardHeader
            title="Montessori Learning Goals"
            action={<EyeIcon className="h-5 w-5 text-slate-300" />}
          />
          <div className="px-5 pb-5 mt-2 space-y-3">
            {learningGoals.map((goal, index) => (
              <div key={goal} className="flex items-start gap-3">
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-emerald-50 dark:bg-emerald-500/15 text-emerald-600 text-xs font-bold">
                  {index + 1}
                </span>
                <p className="text-sm text-slate-600 dark:text-slate-300">{goal}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function PeriodRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 px-3.5 py-3">
      <span className="text-sm text-slate-500 dark:text-slate-400">{label}</span>
      <Badge tone="brand">{value}</Badge>
    </div>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(value));
}
