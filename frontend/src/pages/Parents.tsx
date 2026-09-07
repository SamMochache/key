import React, { useEffect, useState } from 'react';
import { CheckCircle2Icon, Loader2Icon, PlusIcon, SearchIcon, UserRoundIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { EmptyState } from '../components/ui/EmptyState';
import { useApp } from '../context/AppContext';
import { listSchools, listStudents, type ApiStudent, type School } from '../lib/api';
import { createParent, listParents, type ApiParent } from '../lib/parentsApi';

export function Parents() {
  const { role, school } = useApp();
  const [parents, setParents] = useState<ApiParent[]>([]);
  const [students, setStudents] = useState<ApiStudent[]>([]);
  const [schools, setSchools] = useState<School[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone_number: '', password: '', school: '', student: '', relationship: 'PARENT' });

  const load = async () => {
    setError('');
    try {
      const [parentData, studentData] = await Promise.all([listParents(search), listStudents({ isActive: true })]);
      setParents(parentData.results);
      setStudents(studentData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load parent accounts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [search]);

  useEffect(() => {
    if (role !== 'admin') {
      setSchools(school ? [school] : []);
      setForm((current) => ({ ...current, school: school?.id || '' }));
      return;
    }
    listSchools().then(setSchools).catch(() => setSchools([]));
  }, [role, school]);

  const save = async () => {
    if (!form.first_name || !form.last_name || !form.email || !form.school || !form.student) {
      setError('First name, last name, email, school, and student are required.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await createParent({ ...form });
      setForm({ first_name: '', last_name: '', email: '', phone_number: '', password: '', school: school?.id || '', student: '', relationship: 'PARENT' });
      setShowForm(false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create or link the parent account.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <PageHeader title="Parents & Guardians" description="Create parent accounts and explicitly link them to the learners they are authorized to access." actions={<Button onClick={() => setShowForm(true)}><PlusIcon className="h-4 w-4" /> Add parent</Button>} />
      {error && <Card className="mb-5 p-4 border-rose-200 dark:border-rose-900"><p className="text-sm text-rose-600 dark:text-rose-400">{error}</p></Card>}
      {showForm && <Card className="p-5 mb-6">
        <div className="flex items-center gap-3 mb-5"><div className="h-10 w-10 rounded-2xl bg-brand-50 dark:bg-brand-500/10 flex items-center justify-center"><UserRoundIcon className="h-5 w-5 text-brand-600" /></div><div><h2 className="font-display font-bold text-slate-800 dark:text-slate-100">Create or link parent account</h2><p className="text-xs text-slate-400">Use an existing parent email to link another learner. A password is only required for a new account.</p></div></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field label="First name"><input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /></Field>
          <Field label="Last name"><input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /></Field>
          <Field label="Email"><input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></Field>
          <Field label="Phone"><input value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} /></Field>
          <Field label="Initial password (new account)"><input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></Field>
          <Field label="Relationship"><select value={form.relationship} onChange={(e) => setForm({ ...form, relationship: e.target.value })}><option value="PARENT">Parent</option><option value="GUARDIAN">Guardian</option><option value="SPONSOR">Sponsor</option><option value="OTHER">Other</option></select></Field>
          <Field label="School"><select value={form.school} onChange={(e) => setForm({ ...form, school: e.target.value, student: '' })} disabled={role !== 'admin'}><option value="">Select school</option>{schools.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></Field>
          <Field label="Learner"><select value={form.student} onChange={(e) => setForm({ ...form, student: e.target.value })}><option value="">Select learner</option>{students.filter((item) => !form.school || item.school === form.school).map((item) => <option key={item.id} value={item.id}>{item.full_name} — {item.admission_number}</option>)}</select></Field>
        </div>
        <div className="flex justify-end gap-2 mt-5"><Button variant="secondary" onClick={() => setShowForm(false)}>Cancel</Button><Button onClick={save} disabled={saving}>{saving ? <Loader2Icon className="h-4 w-4 animate-spin" /> : <CheckCircle2Icon className="h-4 w-4" />}{saving ? 'Saving…' : 'Save account link'}</Button></div>
      </Card>}
      <Card className="overflow-hidden">
        <div className="p-4 border-b border-slate-100 dark:border-slate-800"><div className="relative max-w-md"><SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search parents…" className="w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 pl-9 pr-3 py-2.5 text-sm" /></div></div>
        {loading && <div className="p-10 flex justify-center"><Loader2Icon className="h-7 w-7 animate-spin text-brand-600" /></div>}
        {!loading && parents.length === 0 && <EmptyState icon="Users" title="No parent accounts" description="Create a parent or guardian account and link it to a learner." />}
        {!loading && parents.length > 0 && <div className="divide-y divide-slate-100 dark:divide-slate-800">{parents.map((parent) => <div key={parent.id} className="p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4"><div><div className="flex items-center gap-2"><p className="font-display font-bold text-slate-800 dark:text-slate-100">{parent.full_name}</p><Badge tone={parent.is_active ? 'emerald' : 'rose'}>{parent.is_active ? 'Active' : 'Inactive'}</Badge></div><p className="text-sm text-slate-500 mt-1">{parent.email} · {parent.phone_number || 'No phone'}</p><p className="text-xs text-slate-400 mt-2">{parent.school_name}</p></div><div className="flex flex-wrap gap-2">{parent.students.map((item) => <span key={item.id} className="rounded-full bg-slate-100 dark:bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300">{item.name} · {item.relationship === 'GUARDIAN' ? 'Guardian' : 'Parent'}</span>)}</div></div>)}</div>}
      </Card>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="block"><span className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">{label}</span>{React.cloneElement(children as React.ReactElement<any>, { className: 'w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2.5 text-sm text-slate-800 dark:text-slate-100' })}</label>;
}
