import React, { useEffect, useState } from 'react';
import { SearchIcon, UserPlusIcon, PencilIcon, UserCheckIcon, UserXIcon, XIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { useApp } from '../context/AppContext';
import { listSchools, listTeachers, listDepartments, createTeacher, updateTeacher, listAcademicYears, listTerms, listSubjects, listClassrooms, type ApiTeacher, type ApiDepartment, type School, type ApiAcademicYear, type ApiTerm, type ApiSubject, type ApiClassroom } from '../lib/api';
import { listTeacherSubjects, createTeacherSubject, updateTeacherSubject, type ApiTeacherSubject } from '../lib/timetableApi';

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
  const [assignments, setAssignments] = useState<ApiTeacherSubject[]>([]);
  const [years, setYears] = useState<ApiAcademicYear[]>([]);
  const [terms, setTerms] = useState<ApiTerm[]>([]);
  const [subjects, setSubjects] = useState<ApiSubject[]>([]);
  const [classrooms, setClassrooms] = useState<ApiClassroom[]>([]);
  const [assignmentOpen, setAssignmentOpen] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState<ApiTeacherSubject | null>(null);
  const [assignmentSaving, setAssignmentSaving] = useState(false);
  const [assignmentError, setAssignmentError] = useState('');
  const [assignmentForm, setAssignmentForm] = useState({ teacher: '', subject: '', classroom: '', role: 'LEAD', start_date: new Date().toISOString().slice(0, 10), end_date: '' });

  const load = async () => {
    setLoadState('loading'); setError('');
    try { setTeachers(await listTeachers({ search: q })); setLoadState('ready'); }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to load teachers.'); setLoadState('error'); }
  };
  useEffect(() => { const t = window.setTimeout(() => void load(), q ? 250 : 0); return () => window.clearTimeout(t); }, [q]);
  useEffect(() => { if (!isAdmin) return; Promise.all([listSchools(), listDepartments()]).then(([s, d]) => { setSchools(s); setDepartments(d); }).catch(() => undefined); }, [isAdmin]);
  const loadAssignments = async () => {
    try {
      const [a, y, t, sub, cls] = await Promise.all([
        listTeacherSubjects(), listAcademicYears(), listTerms(), listSubjects({ active: true }), listClassrooms({ active: true }),
      ]);
      setAssignments(a); setYears(y); setTerms(t); setSubjects(sub); setClassrooms(cls);
    } catch (err) { setAssignmentError(err instanceof Error ? err.message : 'Unable to load teaching assignments.'); }
  };
  useEffect(() => { if (isAdmin) void loadAssignments(); }, [isAdmin]);

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
  const openAssignmentCreate = () => {
    setEditingAssignment(null);
    setAssignmentForm({ teacher: teachers.find((t) => t.is_active)?.id || '', subject: subjects[0]?.id || '', classroom: classrooms[0]?.id || '', role: 'LEAD', start_date: new Date().toISOString().slice(0, 10), end_date: '' });
    setAssignmentError(''); setAssignmentOpen(true);
  };
  const openAssignmentEdit = (item: ApiTeacherSubject) => {
    setEditingAssignment(item);
    setAssignmentForm({ teacher: item.teacher, subject: item.subject, classroom: item.classroom, role: item.role, start_date: item.start_date, end_date: item.end_date || '' });
    setAssignmentError(''); setAssignmentOpen(true);
  };
  const saveAssignment = async (e: React.FormEvent) => {
    e.preventDefault(); setAssignmentSaving(true); setAssignmentError('');
    try {
      const classroom = classrooms.find((item) => item.id === assignmentForm.classroom);
      if (!classroom) throw new Error('Select an active classroom.');
      const payload = { ...assignmentForm, academic_year: classroom.academic_year, term: classroom.term, end_date: assignmentForm.end_date || null, is_active: true };
      if (editingAssignment) await updateTeacherSubject(editingAssignment.id, payload);
      else await createTeacherSubject(payload);
      setAssignmentOpen(false); await loadAssignments();
    } catch (err) { setAssignmentError(err instanceof Error ? err.message : 'Unable to save teaching assignment.'); }
    finally { setAssignmentSaving(false); }
  };
  const toggleAssignment = async (item: ApiTeacherSubject) => {
    setAssignmentError('');
    try { await updateTeacherSubject(item.id, { is_active: !item.is_active }); await loadAssignments(); }
    catch (err) { setAssignmentError(err instanceof Error ? err.message : 'Unable to update assignment.'); }
  };

  return <div>
    <PageHeader title="Teachers" description="The guides, mentors, and educators shaping each learning community." actions={isAdmin ? <Button onClick={openCreate}><UserPlusIcon className="h-4 w-4" /> Add teacher</Button> : undefined} />
    {error && !open && <div className="mb-4 rounded-2xl bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-300">{error}</div>}
    <Card className="overflow-hidden">
      <div className="flex items-center gap-3 p-4 border-b border-slate-100 dark:border-slate-800"><div className="flex items-center gap-2 flex-1 rounded-2xl bg-slate-100 dark:bg-slate-800 px-3 py-2"><SearchIcon className="h-4 w-4 text-slate-400" /><input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search by name, employee no…" className="flex-1 bg-transparent text-sm outline-none text-slate-700 dark:text-slate-200" /></div></div>
      {loadState === 'error' ? <div className="p-8 text-center text-sm text-slate-500">Unable to load teachers</div> : loadState === 'loading' ? <div className="p-8 text-center text-sm text-slate-500">Loading teachers…</div> : teachers.length === 0 ? <div className="p-8 text-center text-sm text-slate-500">No teachers found{q ? ` matching “${q}”` : ''}.</div> :
        <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="text-left text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800"><th className="px-5 py-3">Teacher</th><th className="px-5 py-3">Employee No.</th><th className="px-5 py-3 hidden md:table-cell">Department</th><th className="px-5 py-3 hidden lg:table-cell">Employment</th><th className="px-5 py-3">Status</th>{isAdmin && <th className="px-5 py-3 text-right">Actions</th>}</tr></thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">{teachers.map((teacher) => <tr key={teacher.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"><td className="px-5 py-3"><div className="flex items-center gap-3"><Avatar name={teacher.full_name} size={40} /><div><p className="font-semibold text-slate-800 dark:text-slate-100">{teacher.full_name}</p><p className="text-xs text-slate-400">{teacher.email}</p></div></div></td><td className="px-5 py-3 text-slate-600 dark:text-slate-300">{teacher.employee_number}</td><td className="px-5 py-3 hidden md:table-cell text-slate-600 dark:text-slate-300">{teacher.department_name}</td><td className="px-5 py-3 hidden lg:table-cell text-slate-600 dark:text-slate-300">{teacher.employment_type.replaceAll('_', ' ')}</td><td className="px-5 py-3"><Badge tone={statusTone[teacher.status] ?? 'slate'}>{teacher.status.replaceAll('_', ' ')}</Badge></td>{isAdmin && <td className="px-5 py-3"><div className="flex justify-end gap-2"><Button variant="ghost" onClick={() => openEdit(teacher)} aria-label="Edit teacher"><PencilIcon className="h-4 w-4" /></Button><Button variant="ghost" onClick={() => void toggle(teacher)} aria-label={teacher.is_active ? 'Deactivate teacher' : 'Activate teacher'}>{teacher.is_active ? <UserXIcon className="h-4 w-4" /> : <UserCheckIcon className="h-4 w-4" />}</Button></div></td>}</tr>)}</tbody></table></div>}
    </Card>

    {isAdmin && <section className="mt-6 space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="font-display text-lg font-extrabold text-slate-900 dark:text-white">Teacher–subject assignments</h2><p className="text-sm text-slate-500">Assign a teacher to teach a subject in a classroom for its academic year and term.</p></div><Button onClick={openAssignmentCreate}><UserPlusIcon className="h-4 w-4" /> Create assignment</Button></div>
      {assignmentError && !assignmentOpen && <div className="rounded-2xl bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-300">{assignmentError}</div>}
      <Card className="overflow-x-auto">
        {assignments.length === 0 ? <div className="p-8 text-center text-sm text-slate-500">No teacher–subject assignments yet. Create one to make teachers and subjects available in the timetable.</div> :
        <table className="w-full text-sm"><thead><tr className="text-left text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800"><th className="px-4 py-3">Teacher</th><th className="px-4 py-3">Subject</th><th className="px-4 py-3">Classroom</th><th className="px-4 py-3">Academic period</th><th className="px-4 py-3">Role</th><th className="px-4 py-3">Status</th><th className="px-4 py-3 text-right">Actions</th></tr></thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">{assignments.map((item) => <tr key={item.id}><td className="px-4 py-3 font-semibold">{item.teacher_name}</td><td className="px-4 py-3">{item.subject_name}</td><td className="px-4 py-3">{item.classroom_name}</td><td className="px-4 py-3">{item.academic_year_name} · Term {item.term_number}</td><td className="px-4 py-3">{item.role === 'LEAD' ? 'Lead teacher' : 'Assistant teacher'}</td><td className="px-4 py-3"><Badge tone={item.is_active ? 'emerald' : 'slate'}>{item.is_active ? 'Active' : 'Inactive'}</Badge></td><td className="px-4 py-3"><div className="flex justify-end gap-2"><Button variant="ghost" onClick={() => openAssignmentEdit(item)} aria-label="Edit assignment"><PencilIcon className="h-4 w-4" /></Button><Button variant="ghost" onClick={() => void toggleAssignment(item)} aria-label={item.is_active ? 'Deactivate assignment' : 'Activate assignment'}>{item.is_active ? <UserXIcon className="h-4 w-4" /> : <UserCheckIcon className="h-4 w-4" />}</Button></div></td></tr>)}</tbody></table>}
      </Card>
    </section>}
    {assignmentOpen && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4" onMouseDown={(e) => { if (e.target === e.currentTarget) setAssignmentOpen(false); }}><Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-0"><div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 px-6 py-4"><div><h2 className="font-display text-xl font-extrabold">{editingAssignment ? 'Edit teaching assignment' : 'Create teaching assignment'}</h2><p className="text-sm text-slate-400">Choose the teacher, subject and classroom. The academic year and term follow the classroom.</p></div><button onClick={() => setAssignmentOpen(false)} className="rounded-xl p-2 text-slate-400 hover:bg-slate-100"><XIcon className="h-5 w-5" /></button></div>
      <form onSubmit={saveAssignment} className="p-6 space-y-4"><div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Teacher"><select required value={assignmentForm.teacher} onChange={(e) => setAssignmentForm((f) => ({ ...f, teacher: e.target.value }))}><option value="">Select teacher</option>{teachers.filter((t) => t.is_active && t.status === 'ACTIVE').map((t) => <option key={t.id} value={t.id}>{t.full_name}</option>)}</select></Field>
        <Field label="Subject"><select required value={assignmentForm.subject} onChange={(e) => setAssignmentForm((f) => ({ ...f, subject: e.target.value }))}><option value="">Select subject</option>{subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}</select></Field>
        <Field label="Classroom"><select required value={assignmentForm.classroom} onChange={(e) => setAssignmentForm((f) => ({ ...f, classroom: e.target.value }))}><option value="">Select classroom</option>{classrooms.map((cl) => <option key={cl.id} value={cl.id}>{cl.name} · {cl.academic_year_name} · Term {cl.term_number}</option>)}</select></Field>
        <Field label="Teacher role"><select value={assignmentForm.role} onChange={(e) => setAssignmentForm((f) => ({ ...f, role: e.target.value }))}><option value="LEAD">Lead teacher</option><option value="ASSISTANT">Assistant teacher</option></select></Field>
        <Field label="Start date"><input required type="date" value={assignmentForm.start_date} onChange={(e) => setAssignmentForm((f) => ({ ...f, start_date: e.target.value }))} /></Field>
        <Field label="End date (optional)"><input type="date" value={assignmentForm.end_date} onChange={(e) => setAssignmentForm((f) => ({ ...f, end_date: e.target.value }))} /></Field>
      </div>
      {assignmentError && <div className="rounded-2xl bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-300">{assignmentError}</div>}
      <div className="flex justify-end gap-3 pt-2"><Button type="button" variant="secondary" onClick={() => setAssignmentOpen(false)}>Cancel</Button><Button type="submit" disabled={assignmentSaving || !teachers.length || !subjects.length || !classrooms.length}>{assignmentSaving ? 'Saving…' : editingAssignment ? 'Save changes' : 'Create assignment'}</Button></div></form></Card></div>}
    {open && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4" onMouseDown={(e) => { if (e.target === e.currentTarget) setOpen(false); }}><Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto p-0"><div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 px-6 py-4"><div><h2 className="font-display text-xl font-extrabold text-slate-900 dark:text-white">{editing ? 'Edit teacher' : 'Add teacher'}</h2><p className="text-sm text-slate-400">{editing ? 'Update employment and account details.' : 'Create the teacher profile and login account.'}</p></div><button onClick={() => setOpen(false)} className="rounded-xl p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"><XIcon className="h-5 w-5" /></button></div>
      <form onSubmit={save} className="p-6 space-y-5"><div className="grid grid-cols-1 sm:grid-cols-2 gap-4"><Field label="First name"><input required value={form.first_name} onChange={(e) => set('first_name', e.target.value)} /></Field><Field label="Last name"><input required value={form.last_name} onChange={(e) => set('last_name', e.target.value)} /></Field><Field label="Email"><input required type="email" value={form.account_email} onChange={(e) => set('account_email', e.target.value)} /></Field><Field label="Phone"><input value={form.phone_number} onChange={(e) => set('phone_number', e.target.value)} /></Field><Field label="Employee number"><input required value={form.employee_number} onChange={(e) => set('employee_number', e.target.value)} /></Field><Field label="Employment date"><input required type="date" value={form.employment_date} onChange={(e) => set('employment_date', e.target.value)} /></Field><Field label="Employment type"><select value={form.employment_type} onChange={(e) => set('employment_type', e.target.value)}><option value="FULL_TIME">Full Time</option><option value="PART_TIME">Part Time</option><option value="CONTRACT">Contract</option><option value="INTERN">Intern</option></select></Field><Field label="Status"><select value={form.status} onChange={(e) => set('status', e.target.value)}><option value="ACTIVE">Active</option><option value="ON_LEAVE">On Leave</option><option value="SUSPENDED">Suspended</option><option value="RESIGNED">Resigned</option><option value="RETIRED">Retired</option></select></Field>
          <Field label="Institution"><select required disabled={!!editing} value={form.school} onChange={(e) => { set('school', e.target.value); set('department', ''); }}><option value="">Select institution</option>{schools.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}</select></Field><Field label="Department"><select value={form.department} onChange={(e) => set('department', e.target.value)}><option value="">Select department</option>{departments.filter((d) => d.school === form.school && d.is_active).map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}</select></Field></div>
        <Field label={editing ? 'New password (optional)' : 'Temporary password'}><input required={!editing} minLength={8} type="password" value={form.password} onChange={(e) => set('password', e.target.value)} placeholder={editing ? 'Leave blank to keep current password' : 'At least 8 characters'} /></Field>
        {error && <div className="rounded-2xl bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-300">{error}</div>}<div className="flex justify-end gap-3 pt-2"><Button type="button" variant="secondary" onClick={() => setOpen(false)}>Cancel</Button><Button type="submit" disabled={saving}>{saving ? 'Saving…' : editing ? 'Save changes' : 'Create teacher'}</Button></div></form></Card></div>}
  </div>;
}
function Field({ label, children }: { label: string; children: React.ReactNode }) { return <label className="block text-sm font-semibold text-slate-600 dark:text-slate-300">{label}<span className="mt-1.5 block">{React.cloneElement(children as React.ReactElement, { className: 'w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-brand-200' })}</span></label>; }
