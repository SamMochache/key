import React, { useEffect, useState } from 'react';
import { SearchIcon, UserPlusIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { listTeachers, type ApiTeacher } from '../lib/api';

const statusTone = {
  ACTIVE: 'emerald',
  ON_LEAVE: 'warm',
  SUSPENDED: 'slate',
  RESIGNED: 'slate',
  RETIRED: 'slate'
} as const;

type LoadState = 'loading' | 'ready' | 'error';

export function Teachers() {
  const [q, setQ] = useState('');
  const [teachers, setTeachers] = useState<ApiTeacher[]>([]);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    setLoadState('loading');
    setError('');
    const timer = window.setTimeout(async () => {
      try {
        const data = await listTeachers({ search: q });
        if (cancelled) return;
        setTeachers(data);
        setLoadState('ready');
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Unable to load teachers.');
        setLoadState('error');
      }
    }, q ? 250 : 0);
    return () => { cancelled = true; window.clearTimeout(timer); };
  }, [q]);

  return (
    <div>
      <PageHeader
        title="Teachers"
        description="The guides, mentors, and educators shaping each learning community."
        actions={<Button><UserPlusIcon className="h-4 w-4" /> Add teacher</Button>}
      />
      <Card className="overflow-hidden">
        <div className="flex items-center gap-3 p-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2 flex-1 rounded-2xl bg-slate-100 dark:bg-slate-800 px-3 py-2">
            <SearchIcon className="h-4 w-4 text-slate-400" />
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search by name, employee no…" className="flex-1 bg-transparent text-sm outline-none text-slate-700 dark:text-slate-200" />
          </div>
        </div>
        {loadState === 'error' ? (
          <div className="p-8 text-center text-sm text-slate-500 dark:text-slate-400"><p className="font-semibold text-slate-700 dark:text-slate-200">Unable to load teachers</p><p className="mt-1">{error}</p></div>
        ) : loadState === 'loading' ? (
          <div className="p-8 text-center text-sm text-slate-500 dark:text-slate-400">Loading teachers…</div>
        ) : teachers.length === 0 ? (
          <div className="p-8 text-center text-sm text-slate-500 dark:text-slate-400">No teachers found{q ? ` matching “${q}”` : ''}.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="text-left text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800">
                <th className="px-5 py-3">Teacher</th><th className="px-5 py-3">Employee No.</th><th className="px-5 py-3 hidden md:table-cell">Department</th><th className="px-5 py-3 hidden lg:table-cell">Employment</th><th className="px-5 py-3">Status</th>
              </tr></thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {teachers.map((teacher) => (
                  <tr key={teacher.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                    <td className="px-5 py-3"><div className="flex items-center gap-3"><Avatar name={teacher.full_name} size={40} /><div><p className="font-semibold text-slate-800 dark:text-slate-100">{teacher.full_name}</p><p className="text-xs text-slate-400">{teacher.email}</p></div></div></td>
                    <td className="px-5 py-3 text-slate-600 dark:text-slate-300">{teacher.employee_number}</td>
                    <td className="px-5 py-3 hidden md:table-cell text-slate-600 dark:text-slate-300">{teacher.department_name}</td>
                    <td className="px-5 py-3 hidden lg:table-cell text-slate-600 dark:text-slate-300">{teacher.employment_type.replaceAll('_', ' ')}</td>
                    <td className="px-5 py-3"><Badge tone={statusTone[teacher.status] ?? 'slate'}>{teacher.status.replaceAll('_', ' ')}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
