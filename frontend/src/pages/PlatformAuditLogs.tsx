import React, { useEffect, useState } from 'react';
import { FileClock, RefreshCw } from 'lucide-react';
import { listPlatformAuditLogs, type PlatformAuditLog } from '../lib/platformApi';

export function PlatformAuditLogs() {
  const [logs, setLogs] = useState<PlatformAuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const load = async () => { setLoading(true); try { setLogs((await listPlatformAuditLogs()).results); } catch (err) { setError(err instanceof Error ? err.message : 'Unable to load audit logs.'); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);
  return <div className="space-y-6"><section className="flex items-end justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-600">Security & operations</p><h1 className="mt-2 text-3xl font-extrabold">Audit logs</h1><p className="mt-2 text-sm text-slate-500">A trace of platform-level administrative actions.</p></div><button onClick={load} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-bold dark:border-slate-800 dark:bg-slate-900"><RefreshCw className="h-4 w-4" /> Refresh</button></section>
    {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{error}</div>}
    <section className="overflow-hidden rounded-3xl border border-slate-200/80 bg-white shadow-soft dark:border-slate-800 dark:bg-slate-900"><div className="hidden grid-cols-[180px_1.2fr_1fr_1fr] gap-4 border-b border-slate-100 px-6 py-4 text-xs font-bold uppercase tracking-wide text-slate-400 md:grid dark:border-slate-800"><span>Time</span><span>Action</span><span>Actor</span><span>Scope</span></div><div className="divide-y divide-slate-100 dark:divide-slate-800">{loading ? <div className="px-6 py-12 text-center text-sm text-slate-500">Loading activity…</div> : logs.map((log) => <div key={log.id} className="grid gap-3 px-6 py-5 md:grid-cols-[180px_1.2fr_1fr_1fr] md:items-center"><div className="text-xs text-slate-500">{new Date(log.created_at).toLocaleString()}</div><div className="flex items-start gap-3"><FileClock className="mt-0.5 h-4 w-4 shrink-0 text-brand-600" /><div><p className="font-bold">{log.action.replaceAll('_',' ')}</p><p className="mt-1 text-xs text-slate-400">{log.resource_type} · {log.resource_id}</p></div></div><div><p className="text-sm font-semibold">{log.actor}</p><p className="text-xs text-slate-500">{log.actor_email || 'System'}</p></div><span className="text-sm text-slate-600 dark:text-slate-300">{log.school || 'Platform-wide'}</span></div>)}{!loading && logs.length === 0 && <div className="px-6 py-12 text-center text-sm text-slate-500">No audit events have been recorded yet.</div>}</div></section>
  </div>;
}
