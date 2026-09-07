import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { MoreHorizontalIcon, SearchIcon, UserPlusIcon, XIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import {
  activateStudent,
  createStudent,
  deactivateStudent,
  listSchools,
  listStudents,
  updateStudent,
  type ApiStudent,
  type School
} from '../lib/api';
import { useApp } from '../context/AppContext';

type LoadState = 'loading' | 'ready' | 'error';
type StudentForm = {
  first_name: string;
  last_name: string;
  account_email: string;
  password: string;
  phone_number: string;
  admission_number: string;
  admission_date: string;
  date_of_birth: string;
  gender: string;
  nationality: string;
  birth_certificate_number: string;
};

const emptyForm: StudentForm = {
  first_name: '', last_name: '', account_email: '', password: '', phone_number: '',
  admission_number: '', admission_date: new Date().toISOString().slice(0, 10),
  date_of_birth: '', gender: '', nationality: '', birth_certificate_number: ''
};

function Field({ label, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <label className="block text-sm">
      <span className="mb-1.5 block font-semibold text-slate-700 dark:text-slate-200">{label}</span>
      <input {...props} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-brand-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100" />
    </label>
  );
}

export function Students() {
  const { role, school } = useApp();
  const isAdmin = role === 'admin';
  const [q, setQ] = useState('');
  const [students, setStudents] = useState<ApiStudent[]>([]);
  const [schools, setSchools] = useState<School[]>([]);
  const [schoolId, setSchoolId] = useState('');
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<ApiStudent | null>(null);
  const [form, setForm] = useState<StudentForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [actionId, setActionId] = useState<string | null>(null);
  const [actionError, setActionError] = useState('');

  const loadStudents = async () => {
    try {
      setLoadState('loading');
      setError('');
      setStudents(await listStudents({ search: q }));
      setLoadState('ready');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load students.');
      setLoadState('error');
    }
  };

  useEffect(() => {
    const timer = window.setTimeout(() => { loadStudents(); }, q ? 250 : 0);
    return () => window.clearTimeout(timer);
  }, [q]);

  useEffect(() => {
    if (!isAdmin) return;
    listSchools().then(setSchools).catch(() => undefined);
  }, [isAdmin]);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setSchoolId(school?.id || '');
    setActionError('');
    setModalOpen(true);
  };

  const openEdit = (student: ApiStudent) => {
    setEditing(student);
    setSchoolId(student.school);
    setForm({
      ...emptyForm,
      first_name: student.full_name.split(' ')[0] || '',
      last_name: student.full_name.split(' ').slice(1).join(' '),
      account_email: student.email,
      admission_number: student.admission_number,
      admission_date: student.admission_date,
      date_of_birth: student.date_of_birth,
      gender: student.gender,
      nationality: student.nationality,
      birth_certificate_number: student.birth_certificate_number
    });
    setActionError('');
    setModalOpen(true);
  };

  const setField = (field: keyof StudentForm, value: string) => setForm((current) => ({ ...current, [field]: value }));

  const saveStudent = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setActionError('');
    try {
      if (editing) {
        await updateStudent(editing.id, {
          first_name: form.first_name,
          last_name: form.last_name,
          account_email: form.account_email,
          ...(form.password ? { password: form.password } : {}),
          phone_number: form.phone_number,
          admission_number: form.admission_number,
          admission_date: form.admission_date,
          date_of_birth: form.date_of_birth,
          gender: form.gender,
          nationality: form.nationality,
          birth_certificate_number: form.birth_certificate_number
        });
      } else {
        const targetSchool = schoolId || school?.id;
        if (!targetSchool) throw new Error('Select an institution before creating the student.');
        await createStudent({
          school: targetSchool,
          ...form,
          is_active: true
        });
      }
      setModalOpen(false);
      await loadStudents();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Unable to save student.');
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (student: ApiStudent) => {
    setActionId(student.id);
    setActionError('');
    try {
      if (student.is_active) await deactivateStudent(student.id);
      else await activateStudent(student.id);
      await loadStudents();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Unable to update student status.');
    } finally {
      setActionId(null);
    }
  };

  return (
    <div>
      <PageHeader
        title="Students"
        description="Every child, cared for as an individual. Browse profiles, growth, and enrolment."
        actions={isAdmin ? <Button onClick={openCreate}><UserPlusIcon className="h-4 w-4" /> Enroll student</Button> : undefined}
      />

      {actionError && !modalOpen && (
        <div className="mb-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-900/50 dark:bg-rose-950/30 dark:text-rose-300">{actionError}</div>
      )}

      <Card className="overflow-hidden">
        <div className="flex flex-col items-center gap-3 border-b border-slate-100 p-4 sm:flex-row dark:border-slate-800">
          <div className="flex w-full flex-1 items-center gap-2 rounded-2xl bg-slate-100 px-3 py-2 dark:bg-slate-800">
            <SearchIcon className="h-4 w-4 text-slate-400" />
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search by name, admission no…" className="flex-1 bg-transparent text-sm text-slate-700 outline-none dark:text-slate-200" />
          </div>
        </div>

        {loadState === 'error' ? (
          <div className="p-8 text-center text-sm text-slate-500 dark:text-slate-400"><p className="font-semibold text-slate-700 dark:text-slate-200">Unable to load students</p><p className="mt-1">{error}</p></div>
        ) : loadState === 'loading' ? (
          <div className="p-8 text-center text-sm text-slate-500 dark:text-slate-400">Loading students…</div>
        ) : students.length === 0 ? (
          <div className="p-8 text-center text-sm text-slate-500 dark:text-slate-400">No students found{q ? ` matching “${q}”` : ''}.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-slate-100 text-left text-xs font-bold uppercase tracking-wider text-slate-400 dark:border-slate-800"><th className="px-5 py-3">Student</th><th className="hidden px-5 py-3 md:table-cell">Class</th><th className="hidden px-5 py-3 lg:table-cell">Attendance</th><th className="px-5 py-3">Status</th>{isAdmin && <th className="px-5 py-3 text-right">Actions</th>}</tr></thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {students.map((student) => (
                  <tr key={student.id} className="group transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <td className="px-5 py-3"><Link to={`/students/${student.id}`} className="flex items-center gap-3"><Avatar name={student.full_name} size={40} /><div><p className="font-semibold text-slate-800 group-hover:text-brand-600 dark:text-slate-100">{student.full_name}</p><p className="text-xs text-slate-400">{student.admission_number} · Age {student.age}</p></div></Link></td>
                    <td className="hidden px-5 py-3 text-slate-600 md:table-cell dark:text-slate-300">—</td>
                    <td className="hidden px-5 py-3 text-slate-300 lg:table-cell">—</td>
                    <td className="px-5 py-3"><Badge tone={student.is_active ? 'emerald' : 'slate'}>{student.is_active ? 'Enrolled' : 'Inactive'}</Badge></td>
                    {isAdmin && <td className="px-5 py-3 text-right"><div className="flex justify-end gap-2"><Button variant="ghost" className="px-3" onClick={() => openEdit(student)}>Edit</Button><Button variant="ghost" className="px-3" disabled={actionId === student.id} onClick={() => toggleActive(student)}>{actionId === student.id ? 'Saving…' : student.is_active ? 'Deactivate' : 'Activate'}</Button><Link to={`/students/${student.id}`} className="inline-flex items-center justify-center rounded-xl px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"><MoreHorizontalIcon className="h-4 w-4" /></Link></div></td>}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4" role="dialog" aria-modal="true">
          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-3xl bg-white shadow-2xl dark:bg-slate-900">
            <div className="flex items-center justify-between border-b border-slate-100 px-6 py-5 dark:border-slate-800"><div><h2 className="text-lg font-bold text-slate-900 dark:text-white">{editing ? 'Edit student' : 'Enroll student'}</h2><p className="mt-1 text-sm text-slate-500">{editing ? 'Update the student profile and account.' : 'Create the student profile and sign-in account.'}</p></div><button type="button" onClick={() => setModalOpen(false)} className="rounded-xl p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"><XIcon className="h-5 w-5" /></button></div>
            <form onSubmit={saveStudent} className="space-y-5 p-6">
              {actionError && <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-900/50 dark:bg-rose-950/30 dark:text-rose-300">{actionError}</div>}
              {isAdmin && <label className="block text-sm"><span className="mb-1.5 block font-semibold text-slate-700 dark:text-slate-200">Institution</span><select value={schoolId} onChange={(e) => setSchoolId(e.target.value)} disabled={!!editing} required className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"><option value="">Select institution</option>{schools.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>}
              <div className="grid gap-4 sm:grid-cols-2"><Field label="First name" value={form.first_name} onChange={(e) => setField('first_name', e.target.value)} required /><Field label="Last name" value={form.last_name} onChange={(e) => setField('last_name', e.target.value)} required /><Field label="Email" type="email" value={form.account_email} onChange={(e) => setField('account_email', e.target.value)} required /><Field label={editing ? 'New password (optional)' : 'Temporary password'} type="password" value={form.password} onChange={(e) => setField('password', e.target.value)} required={!editing} minLength={8} /><Field label="Phone" value={form.phone_number} onChange={(e) => setField('phone_number', e.target.value)} /><Field label="Admission number" value={form.admission_number} onChange={(e) => setField('admission_number', e.target.value)} required /><Field label="Admission date" type="date" value={form.admission_date} onChange={(e) => setField('admission_date', e.target.value)} required /><Field label="Date of birth" type="date" value={form.date_of_birth} onChange={(e) => setField('date_of_birth', e.target.value)} required /><label className="block text-sm"><span className="mb-1.5 block font-semibold text-slate-700 dark:text-slate-200">Gender</span><select value={form.gender} onChange={(e) => setField('gender', e.target.value)} required className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"><option value="">Select gender</option><option value="MALE">Male</option><option value="FEMALE">Female</option><option value="OTHER">Other</option></select></label><Field label="Nationality" value={form.nationality} onChange={(e) => setField('nationality', e.target.value)} /><Field label="Birth certificate number" value={form.birth_certificate_number} onChange={(e) => setField('birth_certificate_number', e.target.value)} /></div>
              <div className="flex justify-end gap-3 border-t border-slate-100 pt-5 dark:border-slate-800"><Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button><Button type="submit" disabled={saving}>{saving ? 'Saving…' : editing ? 'Save changes' : 'Create student'}</Button></div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
