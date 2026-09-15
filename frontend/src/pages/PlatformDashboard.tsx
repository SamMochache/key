import React, { useEffect, useState } from 'react';
import { Building2, ShieldCheck, Users, GraduationCap, RefreshCw } from 'lucide-react';
import { listSchools, type School } from '../lib/api';

export function PlatformDashboard() {
  const [schools, setSchools] = useState<School[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadSchools = async () => {
    setLoading(true);
    setError('');
    try {
      setSchools(await listSchools());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load schools.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchools();
  }, []);

  const totalStudents = schools.reduce((sum, school) => sum + school.student_count, 0);
  const totalTeachers = schools.reduce((sum, school) => sum + school.teacher_count, 0);
  const activeSchools = schools.filter((school) => school.is_active).length;

  return (
    <div className="space-y-8">
      <section>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-600 dark:text-brand-400">Platform administration</p>
            <h1 className="mt-2 font-display text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">KEY Platform</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400">
              Manage the institutions connected to KEY. Platform administration is separate from any individual school workspace.
            </p>
          </div>
          <button
            type="button"
            onClick={loadSchools}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-bold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            <RefreshCw className={loading ? 'h-4 w-4 animate-spin' : 'h-4 w-4'} />
            Refresh
          </button>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: 'Institutions', value: schools.length, icon: Building2 },
          { label: 'Active institutions', value: activeSchools, icon: ShieldCheck },
          { label: 'Students', value: totalStudents, icon: GraduationCap },
          { label: 'Teachers', value: totalTeachers, icon: Users },
        ].map(({ label, value, icon: Icon }) => (
          <div key={label} className="rounded-3xl border border-slate-200/80 bg-white p-5 shadow-soft dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-500 dark:text-slate-400">{label}</span>
              <Icon className="h-5 w-5 text-brand-600 dark:text-brand-400" />
            </div>
            <p className="mt-4 font-display text-3xl font-extrabold text-slate-900 dark:text-slate-100">{value}</p>
          </div>
        ))}
      </section>

      <section className="rounded-3xl border border-slate-200/80 bg-white shadow-soft dark:border-slate-800 dark:bg-slate-900">
        <div className="border-b border-slate-100 px-6 py-5 dark:border-slate-800">
          <h2 className="font-display text-lg font-extrabold text-slate-900 dark:text-slate-100">Institutions</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Current schools registered on the platform.</p>
        </div>

        {loading ? (
          <div className="px-6 py-12 text-center text-sm font-semibold text-slate-500">Loading institutions…</div>
        ) : error ? (
          <div className="px-6 py-12 text-center">
            <p className="text-sm font-semibold text-rose-600 dark:text-rose-400">{error}</p>
            <button type="button" onClick={loadSchools} className="mt-4 rounded-2xl bg-brand-600 px-4 py-2.5 text-sm font-bold text-white">Try again</button>
          </div>
        ) : schools.length === 0 ? (
          <div className="px-6 py-12 text-center text-sm text-slate-500">No institutions have been registered yet.</div>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {schools.map((school) => (
              <div key={school.id} className="flex flex-col gap-4 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex min-w-0 items-center gap-4">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-brand-50 font-display text-sm font-extrabold text-brand-700 dark:bg-brand-500/10 dark:text-brand-300">
                    {school.short_name.slice(0, 3)}
                  </div>
                  <div className="min-w-0">
                    <p className="truncate font-bold text-slate-900 dark:text-slate-100">{school.name}</p>
                    <p className="mt-1 truncate text-sm text-slate-500 dark:text-slate-400">{school.city}, {school.country} · {school.email}</p>
                  </div>
                </div>
                <div className="flex shrink-0 items-center gap-5 text-sm">
                  <div><span className="font-bold text-slate-900 dark:text-slate-100">{school.student_count}</span> <span className="text-slate-500">students</span></div>
                  <div><span className="font-bold text-slate-900 dark:text-slate-100">{school.teacher_count}</span> <span className="text-slate-500">teachers</span></div>
                  <span className={`rounded-full px-2.5 py-1 text-xs font-bold ${school.is_active ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'}`}>
                    {school.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
