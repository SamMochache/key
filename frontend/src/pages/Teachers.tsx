import React, { useEffect, useState } from 'react';
import { SearchIcon, UserPlusIcon, PencilIcon, UserCheckIcon, UserXIcon, XIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { useApp } from '../context/AppContext';
import { listSchools, listTeachers, listDepartments, createTeacher, updateTeacher, type ApiTeacher, type ApiDepartment, type School } from '../lib/api';

const statusTone = { ACTIVE: 'emerald', ON_LEAVE: 'warm', SUSPENDED: 'slate', RESIGNED: 'slate', RETIRED: 'slate' } as const;
type Form = { school: string; first_name: string; last_name: string; account_email: string; phone_number: string; password: string; employee_number: string; employment_type: string; employment_date: string; status: string; department: string };
const blank: Form = { school: '', first_name: '', last_name: '', account_email: '', phone_number: '', password: '', employee_number: '', employment_type: 'FULL_TIME', employment_date: new Date().toISOString().slice(0, 10), status: 'ACTIVE', department: '' };

type LoadState = 'loading' | 'ready' | 'error';
export function Teachers() {
  const { role } = useApp();
  const isAdmin = role === 'admin';
  const [q, setQ] = useState('');
  const [teachers, setTeachers] = useState<ApiTeacher[]>([]);
  const [schools, setSchools] = useState<School[]>([]);
  const [departments, setDepartments] = useState<ApiDepartment[]>([]);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [error, setError] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<ApiTeacher | null>(null);
  const [form, setForm] = useState<Form>(blank);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoadState('loading'); setError('');
    try { setTeachers(await listTeachers({ search: q })); setLoadState('ready'); }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to load teachers.'); setLoadState('error'); }
  };
  useEffect(() => { const t = window.setTimeout(() => void load(), q ? 250 : 0); return () => window.clearTimeout(t); }, [q]);
  useEffect(() => { if (!isAdmin) return; Promise.all([listSchools(), listDepartments()]).then(([s, d]) => { setSchools(s); setDepartments(d); }).catch(() => undefined); }, [isAdmin]);

  const openCreate = () => { setEditing(null); setForm({ ...blank, school: schools[0]?.id || '' }); setOpen(true); };
  const openEdit = (teacher: ApiTeacher) => { setEditing(teacher); setForm({ school: teacher.school, first_name: teacher.full_name.split(' ')[0] || '', last_name: teacher.full_name.split(' ').slice(1).join(' '), account_email: teacher.email, phone_number: '', password: '', employee_number: teacher.employee_number, employment_type: teacher.employment_type, employment_date: teacher.employment_date, status: teacher.status, department: teacher.department }); setOpen(true); };
  const set = (key: keyof Form, value: string) => setForm((f) => ({ ...f, [key]: value }));
  const save = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true); setError('');
    try {
      const payload: Record<string, unknown> = { ...form };
      if (editing && !form.password) delete payload.password;
      if (!editing) { if (!form.school) throw new Error('Select an institution.'); }
      await (editing ? updateTeacher(editing.id, payload) : createTeacher(payload));
      setOpen(false); await load();
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to save teacher.'); }
    finally { setSaving(false); }
  };
  const toggle = async (teacher: ApiTeacher) => { setError(''); try { await updateTeacher(teacher.id, { is_active: !teacher.is_active }); await load(); } catch (err) { setError(err instanceof Error ? err.message : 'Unable to update teacher.'); } };

  return <div>
    <PageHeader title="Teachers" description="The guides, mentors, and educators shaping each learning community." actions={isAdmin ? <Button onClick={openCreate}><UserPlusIcon className="h-4 w-4" /> Add teacher</Button> : undefined} />
    {error && !open && <div className="mb-4 rounded-2xl bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-300">{error}</div>}
    <Card className="overflow-hidden">
      <div className="flex items-center gap-3 p-4 border-b border-slate-100 dark:border-slate-800"><div className="flex items-center gap-2 flex-1 rounded-2xl bg-slate-100 dark:bg-slate-800 px-3 py-2"><SearchIcon className="h-4 w-4 text-slate-400" /><input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search by name, employee no…" className="flex-1 bg-transparent text-sm outline-none text-slate-700 dark:text-slate-200" /></div></div>
      {loadState === 'error' ? <div className="p-8 text-center text-sm text-slate-500">Unable to load teachers</div> : loadState === 'loading' ? <div className="p-8 text-center text-sm text-slate-500">Loading teachers…</div> : teachers.length === 0 ? <div className="p-8 text-center text-sm text-slate-500">No teachers found{q ? ` matching “${q}”` : ''}.</div> :
        <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="text-left text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800"><th className="px-5 py-3">Teacher</th><th className="px-5 py-3">Employee No.</th><th className="px-5 py-3 hidden md:table-cell">Department</th><th className="px-5 py-3 hidden lg:table-cell">Employment</th><th className="px-5 py-3">Status</th>{isAdmin && <th className="px-5 py-3 text-right">Actions</th>}</tr></thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">{teachers.map((teacher) => <tr key={teacher.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"><td className="px-5 py-3"><div className="flex items-center gap-3"><Avatar name={teacher.full_name} size={40} /><div><p className="font-semibold text-slate-800 dark:text-slate-100">{teacher.full_name}</p><p className="text-xs text-slate-400">{teacher.email}</p></div></div></td><td className="px-5 py-3 text-slate-600 dark:text-slate-300">{teacher.employee_number}</td><td className="px-5 py-3 hidden md:table-cell text-slate-600 dark:text-slate-300">{teacher.department_name}</td><td className="px-5 py-3 hidden lg:table-cell text-slate-600 dark:text-slate-300">{teacher.employment_type.replaceAll('_', ' ')}</td><td className="px-5 py-3"><Badge tone={statusTone[teacher.status] ?? 'slate'}>{teacher.status.replaceAll('_', ' ')}</Badge></td>{isAdmin && <td className="px-5 py-3"><div className="flex justify-end gap-2"><Button variant="ghost" onClick={() => openEdit(teacher)} aria-label="Edit teacher"><PencilIcon className="h-4 w-4" /></Button><Button variant="ghost" onClick={() => void toggle(teacher)} aria-label={teacher.is_active ? 'Deactivate teacher' : 'Activate teacher'}>{teacher.is_active ? <UserXIcon className="h-4 w-4" /> : <UserCheckIcon className="h-4 w-4" />}</Button></div></td>}</tr>)}</tbody></table></div>}
    </Card>

    {open && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4" onMouseDown={(e) => { if (e.target === e.currentTarget) setOpen(false); }}><Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-0"><div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 px-6 py-4"><div><h2 className="font-display text-xl font-extrabold text-slate-900 dark:text-white">{editing ? 'Edit teacher' : 'Add teacher'}</h2><p className="text-sm text-slate-400">{editing ? 'Update employment and account details.' : 'Create the teacher profile and login account.'}</p></div><button onClick={() => setOpen(false)} className="rounded-xl p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"><XIcon className="h-5 w-5" /></button></div>
      <form onSubmit={save} className="p-6 space-y-5"><div className="grid grid-cols-1 sm:grid-cols-2 gap-4"><Field label="First name"><input required value={form.first_name} onChange={(e) => set('first_name', e.target.value)} /></Field><Field label="Last name"><input required value={form.last_name} onChange={(e) => set('last_name', e.target.value)} /></Field><Field label="Email"><input required type="email" value={form.account_email} onChange={(e) => set('account_email', e.target.value)} /></Field><Field label="Phone"><input value={form.phone_number} onChange={(e) => set('phone_number', e.target.value)} /></Field><Field label="Employee number"><input required value={form.employee_number} onChange={(e) => set('employee_number', e.target.value)} /></Field><Field label="Employment date"><input required type="date" value={form.employment_date} onChange={(e) => set('employment_date', e.target.value)} /></Field><Field label="Employment type"><select value={form.employment_type} onChange={(e) => set('employment_type', e.target.value)}><option value="FULL_TIME">Full Time</option><option value="PART_TIME">Part Time</option><option value="CONTRACT">Contract</option><option value="INTERN">Intern</option></select></Field><Field label="Status"><select value={form.status} onChange={(e) => set('status', e.target.value)}><option value="ACTIVE">Active</option><option value="ON_LEAVE">On Leave</option><option value="SUSPENDED">Suspended</option><option value="RESIGNED">Resigned</option><option value="RETIRED">Retired</option></select></Field>
          <Field label="Institution"><select required disabled={!!editing} value={form.school} onChange={(e) => { set('school', e.target.value); set('department', ''); }}><option value="">Select institution</option>{schools.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}</select></Field><Field label="Department"><select value={form.department} onChange={(e) => set('department', e.target.value)}><option value="">Select department</option>{departments.filter((d) => d.school === form.school && d.is_active).map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}</select></Field></div>
        <Field label={editing ? 'New password (optional)' : 'Temporary password'}><input required={!editing} minLength={8} type="password" value={form.password} onChange={(e) => set('password', e.target.value)} placeholder={editing ? 'Leave blank to keep current password' : 'At least 8 characters'} /></Field>
        {error && <div className="rounded-2xl bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-300">{error}</div>}<div className="flex justify-end gap-3 pt-2"><Button type="button" variant="secondary" onClick={() => setOpen(false)}>Cancel</Button><Button type="submit" disabled={saving}>{saving ? 'Saving…' : editing ? 'Save changes' : 'Create teacher'}</Button></div></form></Card></div>}
  </div>;
}
function Field({ label, children }: { label: string; children: React.ReactNode }) { return <label className="block text-sm font-semibold text-slate-600 dark:text-slate-300">{label}<span className="mt-1.5 block">{React.cloneElement(children as React.ReactElement, { className: 'w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-brand-200' })}</span></label>; }
