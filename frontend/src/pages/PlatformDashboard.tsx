import React, { useEffect, useState } from 'react';
import { Activity, Building2, FileClock, GraduationCap, RefreshCw, ShieldCheck, Users, UsersRound } from 'lucide-react';
import { Link } from 'react-router-dom';
import { listSchools, type School } from '../lib/api';
import { getPlatformSummary, listPlatformAuditLogs, type PlatformAuditLog, type PlatformSummary } from '../lib/platformApi';

export function PlatformDashboard() {
  const [schools, setSchools] = useState<School[]>([]);
  const [summary, setSummary] = useState<PlatformSummary | null>(null);
  const [auditLogs, setAuditLogs] = useState<PlatformAuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [schoolData, summaryData, auditData] = await Promise.all([
        listSchools(),
        getPlatformSummary(),
        listPlatformAuditLogs(),
      ]);
      setSchools(schoolData);
      setSummary(summaryData);
      setAuditLogs(auditData.results.slice(0, 5));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load platform data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const cards = summary ? [
    { label: 'Institutions', value: summary.institutions, icon: Building2 },
    { label: 'Active institutions', value: summary.active_institutions, icon: ShieldCheck },
    { label: 'Students', value: summary.students, icon: GraduationCap },
    { label: 'Teachers', value: summary.teachers, icon: Users },
    { label: 'Parents', value: summary.parents, icon: UsersRound },
    { label: 'Active users', value: summary.users, icon: Activity },
  ] : [];

  return (
    <div className="space-y-8">
      <section>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-600 dark:text-brand-400">Platform control plane</p>
            <h1 className="mt-2 font-display text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">KEY Platform</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400">Operate institutions, users, security activity and platform configuration without entering a school workspace.</p>
          </div>
          <button type="button" onClick={load} disabled={loading} className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-bold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
            <RefreshCw className={loading ? 'h-4 w-4 animate-spin' : 'h-4 w-4'} /> Refresh
          </button>
        </div>
      </section>

      {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700 dark:border-rose-900/50 dark:bg-rose-950/30 dark:text-rose-300">{error}</div>}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map(({ label, value, icon: Icon }) => (
          <div key={label} className="rounded-3xl border border-slate-200/80 bg-white p-5 shadow-soft dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center justify-between"><span className="text-sm font-semibold text-slate-500 dark:text-slate-400">{label}</span><Icon className="h-5 w-5 text-brand-600 dark:text-brand-400" /></div>
            <p className="mt-4 font-display text-3xl font-extrabold text-slate-900 dark:text-slate-100">{loading ? '—' : value}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <div className="rounded-3xl border border-slate-200/80 bg-white shadow-soft dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between border-b border-slate-100 px-6 py-5 dark:border-slate-800">
            <div><h2 className="font-display text-lg font-extrabold text-slate-900 dark:text-slate-100">Institutions</h2><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Current institutions registered on KEY.</p></div>
            <Link to="/platform/institutions" className="text-sm font-bold text-brand-600 hover:underline dark:text-brand-400">Manage all</Link>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {schools.map((school) => (
              <Link key={school.id} to={`/platform/institutions/${school.id}`} className="flex flex-col gap-3 px-6 py-5 transition hover:bg-slate-50 sm:flex-row sm:items-center sm:justify-between dark:hover:bg-slate-800/40">
                <div className="flex min-w-0 items-center gap-4"><div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-brand-50 font-display text-sm font-extrabold text-brand-700 dark:bg-brand-500/10 dark:text-brand-300">{school.short_name.slice(0, 3)}</div><div className="min-w-0"><p className="truncate font-bold text-slate-900 dark:text-slate-100">{school.name}</p><p className="mt-1 truncate text-sm text-slate-500 dark:text-slate-400">{school.city}, {school.country} · {school.email}</p></div></div>
                <div className="flex shrink-0 items-center gap-4 text-sm"><span className="font-semibold text-slate-600 dark:text-slate-300">{school.student_count} students</span><span className="font-semibold text-slate-600 dark:text-slate-300">{school.teacher_count} teachers</span><span className={`rounded-full px-2.5 py-1 text-xs font-bold ${school.is_active ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'}`}>{school.is_active ? 'Active' : 'Inactive'}</span></div>
              </Link>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200/80 bg-white shadow-soft dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between border-b border-slate-100 px-6 py-5 dark:border-slate-800"><div><h2 className="font-display text-lg font-extrabold text-slate-900 dark:text-slate-100">Recent activity</h2><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Administrative events across the platform.</p></div><FileClock className="h-5 w-5 text-brand-600 dark:text-brand-400" /></div>
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {auditLogs.length === 0 ? <div className="px-6 py-10 text-sm text-slate-500">No platform activity has been recorded yet.</div> : auditLogs.map((log) => <div key={log.id} className="px-6 py-4"><p className="text-sm font-bold text-slate-900 dark:text-slate-100">{log.action.replaceAll('_', ' ')}</p><p className="mt-1 text-xs text-slate-500">{log.actor}{log.school ? ` · ${log.school}` : ''}</p><p className="mt-1 text-xs text-slate-400">{new Date(log.created_at).toLocaleString()}</p></div>)}
          </div>
          <div className="border-t border-slate-100 px-6 py-4 dark:border-slate-800"><Link to="/platform/audit-logs" className="text-sm font-bold text-brand-600 hover:underline dark:text-brand-400">View audit log</Link></div>
        </div>
      </section>
    </div>
  );
}
