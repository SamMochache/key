import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { UserPlusIcon, SearchIcon, FilterIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { listStudents, type ApiStudent } from '../lib/api';

const statusTone = {
  Enrolled: 'emerald',
  Pending: 'warm',
  Alumni: 'slate'
} as const;

type LoadState = 'loading' | 'ready' | 'error';

export function Students() {
  const [q, setQ] = useState('');
  const [students, setStudents] = useState<ApiStudent[]>([]);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    setLoadState('loading');
    setError('');

    const timer = window.setTimeout(async () => {
      try {
        const data = await listStudents({ search: q });
        if (cancelled) return;
        setStudents(data);
        setLoadState('ready');
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Unable to load students.');
        setLoadState('error');
      }
    }, q ? 250 : 0);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [q]);

  return (
    <div>
      <PageHeader
        title="Students"
        description="Every child, cared for as an individual. Browse profiles, growth, and enrolment."
        actions={
          <Button>
            <UserPlusIcon className="h-4 w-4" /> Enroll student
          </Button>
        }
      />

      <Card className="overflow-hidden">
        <div className="flex flex-col sm:flex-row items-center gap-3 p-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2 flex-1 w-full rounded-2xl bg-slate-100 dark:bg-slate-800 px-3 py-2">
            <SearchIcon className="h-4 w-4 text-slate-400" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search by name, admission no…"
              className="flex-1 bg-transparent text-sm outline-none text-slate-700 dark:text-slate-200"
            />
          </div>
          <Button variant="secondary" className="w-full sm:w-auto">
            <FilterIcon className="h-4 w-4" /> Filters
          </Button>
        </div>

        {loadState === 'error' ? (
          <div className="p-8 text-center text-sm text-slate-500 dark:text-slate-400">
            <p className="font-semibold text-slate-700 dark:text-slate-200">Unable to load students</p>
            <p className="mt-1">{error}</p>
          </div>
        ) : loadState === 'loading' ? (
          <div className="p-8 text-center text-sm text-slate-500 dark:text-slate-400">Loading students…</div>
        ) : students.length === 0 ? (
          <div className="p-8 text-center text-sm text-slate-500 dark:text-slate-400">
            No students found{q ? ` matching “${q}”` : ''}.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800">
                  <th className="px-5 py-3">Student</th>
                  <th className="px-5 py-3 hidden md:table-cell">Class</th>
                  <th className="px-5 py-3 hidden lg:table-cell">House</th>
                  <th className="px-5 py-3 hidden lg:table-cell">Attendance</th>
                  <th className="px-5 py-3">Growth</th>
                  <th className="px-5 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {students.map((student) => {
                  const status = student.is_active ? 'Enrolled' : 'Pending';
                  return (
                    <tr
                      key={student.id}
                      className="group hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
                    >
                      <td className="px-5 py-3">
                        <Link to={`/students/${student.id}`} className="flex items-center gap-3">
                          <Avatar name={student.full_name} size={40} />
                          <div>
                            <p className="font-semibold text-slate-800 dark:text-slate-100 group-hover:text-brand-600">
                              {student.full_name}
                            </p>
                            <p className="text-xs text-slate-400">
                              {student.admission_number} · Age {student.age}
                            </p>
                          </div>
                        </Link>
                      </td>
                      <td className="px-5 py-3 hidden md:table-cell text-slate-600 dark:text-slate-300">—</td>
                      <td className="px-5 py-3 hidden lg:table-cell text-slate-600 dark:text-slate-300">—</td>
                      <td className="px-5 py-3 hidden lg:table-cell text-slate-300">—</td>
                      <td className="px-5 py-3 text-slate-300">—</td>
                      <td className="px-5 py-3">
                        <Badge tone={statusTone[status]}>{status}</Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
