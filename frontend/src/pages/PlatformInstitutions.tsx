import React, { useEffect, useState } from 'react';
import { Building2, Plus, Search } from 'lucide-react';
import { Link } from 'react-router-dom';
import { createInstitution, type PlatformSchool } from '../lib/platformApi';
import { listSchools, type School } from '../lib/api';

export function PlatformInstitutions() {
  const [schools, setSchools] = useState<School[]>([]);
  const [search, setSearch] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: '', short_name: '', email: '', phone_number: '', address: '', city: '', country: 'Kenya', timezone: 'Africa/Nairobi' });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    try { setSchools(await listSchools()); } catch (err) { setError(err instanceof Error ? err.message : 'Unable to load institutions.'); }
  };
  useEffect(() => { load(); }, []);

  const filtered = schools.filter((school) => `${school.name} ${school.short_name} ${school.city} ${school.email}`.toLowerCase().includes(search.toLowerCase()));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault(); setBusy(true); setError('');
    try {
      await createInstitution(form as Partial<PlatformSchool>);
      setForm({ name: '', short_name: '', email: '', phone_number: '', address: '', city: '', country: 'Kenya', timezone: 'Africa/Nairobi' });
      setShowCreate(false); await load();
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to create institution.'); } finally { setBusy(false); }
  };

  return <div className="space-y-6">
    <section className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-600 dark:text-brand-400">Platform</p><h1 className="mt-2 font-display text-3xl font-extrabold text-slate-900 dark:text-slate-100">Institutions</h1><p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Register, inspect and manage every school connected to KEY.</p></div><button onClick={() => setShowCreate(true)} className="inline-flex items-center justify-center gap-2 rounded-2xl bg-brand-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-brand-700"><Plus className="h-4 w-4" /> Add institution</button></section>
    {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">{error}</div>}
    <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900"><Search className="h-5 w-5 text-slate-400" /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search institutions…" className="w-full bg-transparent text-sm outline-none" /></div>
    <section className="overflow-hidden rounded-3xl border border-slate-200/80 bg-white shadow-soft dark:border-slate-800 dark:bg-slate-900"><div className="divide-y divide-slate-100 dark:divide-slate-800">{filtered.map((school) => <Link key={school.id} to={`/platform/institutions/${school.id}`} className="flex flex-col gap-4 px-6 py-5 transition hover:bg-slate-50 sm:flex-row sm:items-center sm:justify-between dark:hover:bg-slate-800/40"><div className="flex items-center gap-4"><div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-50 font-display font-extrabold text-brand-700 dark:bg-brand-500/10 dark:text-brand-300"><Building2 className="h-5 w-5" /></div><div><p className="font-bold text-slate-900 dark:text-slate-100">{school.name}</p><p className="mt-1 text-sm text-slate-500">{school.short_name} · {school.city}, {school.country}</p></div></div><div className="flex items-center gap-5 text-sm"><span><b>{school.student_count}</b> students</span><span><b>{school.teacher_count}</b> teachers</span><span className={`rounded-full px-2.5 py-1 text-xs font-bold ${school.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>{school.is_active ? 'Active' : 'Inactive'}</span></div></Link>)}{filtered.length === 0 && <div className="px-6 py-12 text-center text-sm text-slate-500">No institutions match your search.</div>}</div></section>
    {showCreate && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4"><form onSubmit={submit} className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white p-6 shadow-2xl dark:bg-slate-900"><div className="flex items-start justify-between"><div><h2 className="text-xl font-extrabold">Add institution</h2><p className="mt-1 text-sm text-slate-500">Create the institution record first; add its administrator from the institution page.</p></div><button type="button" onClick={() => setShowCreate(false)} className="text-slate-400">✕</button></div><div className="mt-6 grid gap-4 sm:grid-cols-2">{Object.entries(form).map(([key, value]) => <label key={key} className={key === 'address' ? 'sm:col-span-2' : ''}><span className="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500">{key.replaceAll('_', ' ')}</span>{key === 'address' ? <textarea value={value} onChange={(e) => setForm({ ...form, [key]: e.target.value })} rows={3} className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-slate-700 dark:bg-slate-950" /> : <input value={value} onChange={(e) => setForm({ ...form, [key]: e.target.value })} required={['name', 'short_name'].includes(key)} className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-slate-700 dark:bg-slate-950" />}</label>)}</div><div className="mt-6 flex justify-end gap-3"><button type="button" onClick={() => setShowCreate(false)} className="rounded-xl px-4 py-2.5 text-sm font-bold">Cancel</button><button disabled={busy} className="rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-bold text-white disabled:opacity-50">{busy ? 'Creating…' : 'Create institution'}</button></div></form></div>}
  </div>;
}
