import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  GlobeIcon, CakeIcon, ArrowLeftIcon, SparklesIcon, GraduationCapIcon,
  PlusIcon, ArrowRightLeftIcon, XIcon
} from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import { cn } from '../lib/utils';
import {
  createEnrollment, getStudent, listAcademicYears, listClassrooms, listEnrollments,
  listTerms, updateEnrollment, type ApiAcademicYear, type ApiClassroom,
  type ApiEnrollment, type ApiStudent, type ApiTerm
} from '../lib/api';

const TABS = ['Overview', 'Enrollment', 'Attendance', 'Assessments', 'Assignments', 'Behaviour', 'Portfolio', 'Teacher Notes', 'AI Reports'];
const selectClass = 'w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-sm text-slate-700 dark:text-slate-200 outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10';

export function StudentProfile() {
  const { id } = useParams();
  const [student, setStudent] = useState<ApiStudent | null>(null);
  const [enrollments, setEnrollments] = useState<ApiEnrollment[]>([]);
  const [tab, setTab] = useState('Overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showEnrollForm, setShowEnrollForm] = useState(false);
  const [years, setYears] = useState<ApiAcademicYear[]>([]);
  const [terms, setTerms] = useState<ApiTerm[]>([]);
  const [classes, setClasses] = useState<ApiClassroom[]>([]);
  const [form, setForm] = useState({ academic_year: '', term: '', classroom: '' });
  const [saving, setSaving] = useState(false);
  const [actionId, setActionId] = useState<string | null>(null);
  const [formError, setFormError] = useState('');

  const loadData = async (studentId: string) => {
    const [studentData, enrollmentData] = await Promise.all([
      getStudent(studentId), listEnrollments({ search: studentId })
    ]);
    setStudent(studentData);
    // The enrollment endpoint's search is name/admission based, not ID based. Keep only this student's records.
    setEnrollments(enrollmentData.filter((item) => item.student === studentId));
  };

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);
    setError('');
    Promise.all([getStudent(id), listEnrollments()])
      .then(([studentData, enrollmentData]) => {
        if (!cancelled) {
          setStudent(studentData);
          setEnrollments(enrollmentData.filter((item) => item.student === id));
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load student.');
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [id]);

  const openEnrollForm = async () => {
    setFormError('');
    setShowEnrollForm(true);
    if (years.length) return;
    try {
      const yearData = await listAcademicYears();
      setYears(yearData);
      const current = yearData.find((year) => year.is_current);
      if (current) {
        setForm((value) => ({ ...value, academic_year: current.id }));
        const termData = await listTerms({ academicYear: current.id });
        setTerms(termData);
        const term = termData.find((item) => item.is_current) || termData[0];
        if (term) {
          setForm((value) => ({ ...value, term: term.id }));
          setClasses(await listClassrooms({ academicYear: current.id, term: term.id, active: true }));
        }
      }
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unable to load enrollment options.');
    }
  };

  const changeYear = async (academic_year: string) => {
    setForm({ academic_year, term: '', classroom: '' });
    setClasses([]);
    setFormError('');
    try {
      setTerms(await listTerms({ academicYear: academic_year }));
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unable to load terms.');
    }
  };

  const changeTerm = async (term: string) => {
    setForm((value) => ({ ...value, term, classroom: '' }));
    setFormError('');
    if (!form.academic_year || !term) return;
    try {
      setClasses(await listClassrooms({ academicYear: form.academic_year, term, active: true }));
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unable to load classes.');
    }
  };

  const submitEnrollment = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!id || !student) return;
    if (!form.academic_year || !form.term || !form.classroom) {
      setFormError('Select an academic year, term, and class.');
      return;
    }
    if (enrollments.some((item) => item.academic_year === form.academic_year && item.term === form.term && item.status === 'ENROLLED')) {
      setFormError('This student is already enrolled for the selected academic year and term.');
      return;
    }
    const classroom = classes.find((item) => item.id === form.classroom);
    if (classroom?.capacity && classroom.student_count >= classroom.capacity) {
      setFormError('This classroom has reached its capacity.');
      return;
    }
    setSaving(true);
    setFormError('');
    try {
      await createEnrollment({
        student: id,
        classroom: form.classroom,
        academic_year: form.academic_year,
        term: form.term,
        enrollment_date: new Date().toISOString().slice(0, 10),
        status: 'ENROLLED'
      });
      setShowEnrollForm(false);
      await loadData(id);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unable to enroll student.');
    } finally { setSaving(false); }
  };

  const withdrawEnrollment = async (enrollment: ApiEnrollment) => {
    if (!window.confirm(`Withdraw ${student?.full_name || 'this student'} from ${enrollment.classroom_name}? Historical enrollment data will be retained.`)) return;
    setActionId(enrollment.id);
    setFormError('');
    try {
      await updateEnrollment(enrollment.id, { status: 'WITHDRAWN' });
      if (id) await loadData(id);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unable to update enrollment.');
    } finally { setActionId(null); }
  };

  if (loading) return <Card className="p-8 text-center text-sm text-slate-500">Loading student…</Card>;
  if (!student) return <Card><EmptyState icon="UserX" title="Student not found" description={error || 'This student is not available to your account.'} action={<Link to="/students"><Button>Back to students</Button></Link>} /></Card>;

  const currentEnrollment = enrollments.find((item) => item.status === 'ENROLLED');
  const status = student.is_active ? 'Enrolled' : 'Pending';

  return (
    <div>
      <Link to="/students" className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-400 hover:text-brand-600 mb-4"><ArrowLeftIcon className="h-4 w-4" /> All students</Link>
      <Card className="p-6 mb-6">
        <div className="flex flex-col sm:flex-row gap-5">
          <Avatar name={student.full_name} size={88} className="ring-4 ring-brand-100 dark:ring-slate-800" />
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap"><h1 className="font-display text-2xl font-extrabold text-slate-900 dark:text-white">{student.full_name}</h1><Badge tone={status === 'Enrolled' ? 'emerald' : 'warm'}>{status}</Badge></div>
            <p className="text-slate-400 mt-0.5">{student.admission_number} · {student.school_name}</p>
            <div className="flex flex-wrap gap-x-6 gap-y-2 mt-4 text-sm"><Meta icon={<CakeIcon className="h-4 w-4" />} label={`${student.date_of_birth} · Age ${student.age}`} /><Meta icon={<GlobeIcon className="h-4 w-4" />} label={student.nationality} /></div>
            {currentEnrollment && <div className="mt-3 inline-flex flex-wrap items-center gap-2 rounded-xl bg-slate-50 px-3 py-2 text-sm dark:bg-slate-800/60"><GraduationCapIcon className="h-4 w-4 text-brand-500" /><span className="font-semibold text-slate-700 dark:text-slate-200">{currentEnrollment.classroom_name}</span><span className="text-slate-400">· {currentEnrollment.academic_year_name} · Term {currentEnrollment.term_number}</span></div>}
          </div>
          <div className="flex sm:flex-col gap-3"><Link to="/ai-reports"><Button className="w-full"><SparklesIcon className="h-4 w-4" /> AI Report</Button></Link><Button variant="secondary">Message parent</Button></div>
        </div>
      </Card>

      <div className="flex gap-1 overflow-x-auto mb-6 rounded-2xl bg-slate-100 dark:bg-slate-800/60 p-1">
        {TABS.map((t) => <button key={t} onClick={() => setTab(t)} className={cn('shrink-0 rounded-xl px-4 py-2 text-sm font-semibold transition-colors', tab === t ? 'bg-white dark:bg-slate-900 text-brand-600 shadow-soft' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300')}>{t}</button>)}
      </div>

      {tab === 'Overview' && <div className="grid grid-cols-1 lg:grid-cols-3 gap-6"><div className="lg:col-span-2 space-y-6"><Card><CardHeader title="Student Information" subtitle="Current profile data" /><div className="grid grid-cols-1 sm:grid-cols-2 gap-4 px-5 pb-5 mt-2 text-sm"><Info label="Email" value={student.email} /><Info label="Gender" value={student.gender} /><Info label="Admission date" value={student.admission_date} /><Info label="Birth certificate" value={student.birth_certificate_number || 'Not provided'} /></div></Card><Card><CardHeader title="Progress Timeline" /><EmptyState icon="Clock" title="No progress activity yet" description="Assessment, attendance, portfolio and teacher activity will appear here as those modules are connected." /></Card></div><div className="space-y-6"><div className="grid grid-cols-2 gap-4"><StatBox label="Attendance" value="—" tone="text-emerald-600" /><StatBox label="Growth Index" value="—" tone="text-brand-600" /></div><Card className="overflow-hidden"><CardHeader title="Latest Portfolio" /><EmptyState icon="Image" title="No portfolio entries yet" /></Card></div></div>}

      {tab === 'Enrollment' && <Card>
        <CardHeader title="Enrollment History" subtitle="Academic placement is preserved as historical records" action={<Button type="button" variant="emerald" onClick={openEnrollForm}><PlusIcon className="h-4 w-4" /> Enroll student</Button>} />
        {showEnrollForm && <form onSubmit={submitEnrollment} className="mx-5 mb-5 rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/50"><div className="grid grid-cols-1 md:grid-cols-3 gap-4"><Field label="Academic year"><select value={form.academic_year} onChange={(e) => changeYear(e.target.value)} className={selectClass} disabled={saving}><option value="">Select year</option>{years.map((year) => <option key={year.id} value={year.id}>{year.name}{year.is_current ? ' · Current' : ''}</option>)}</select></Field><Field label="Term"><select value={form.term} onChange={(e) => changeTerm(e.target.value)} className={selectClass} disabled={saving || !form.academic_year}><option value="">Select term</option>{terms.map((term) => <option key={term.id} value={term.id}>Term {term.term_number}{term.is_current ? ' · Current' : ''}</option>)}</select></Field><Field label="Class"><select value={form.classroom} onChange={(e) => setForm({ ...form, classroom: e.target.value })} className={selectClass} disabled={saving || !form.term}><option value="">Select class</option>{classes.map((item) => <option key={item.id} value={item.id}>{item.name}{item.student_count >= item.capacity ? ' · Full' : ''}</option>)}</select></Field></div>{formError && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{formError}</p>}<div className="flex justify-end gap-3 mt-4"><Button type="button" variant="secondary" onClick={() => setShowEnrollForm(false)} disabled={saving}><XIcon className="h-4 w-4" /> Cancel</Button><Button type="submit" variant="emerald" disabled={saving}>{saving ? 'Enrolling…' : 'Confirm enrollment'}</Button></div></form>}
        <div className="px-5 pb-5">{enrollments.length === 0 ? <EmptyState icon="GraduationCap" title="No enrollment history" description="Enroll the student into an academic year, term, and class to begin their academic record." /> : <div className="divide-y divide-slate-100 dark:divide-slate-800">{enrollments.map((item) => <div key={item.id} className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center"><div className="flex-1 min-w-0"><div className="flex flex-wrap items-center gap-2"><p className="font-semibold text-slate-800 dark:text-slate-100">{item.classroom_name}</p><Badge tone={item.status === 'ENROLLED' ? 'emerald' : 'slate'}>{item.status}</Badge></div><p className="text-sm text-slate-400 mt-1">{item.academic_year_name} · Term {item.term_number} · Enrolled {item.enrollment_date}</p></div>{item.status === 'ENROLLED' && <Button type="button" variant="ghost" className="self-start sm:self-auto" disabled={actionId === item.id} onClick={() => withdrawEnrollment(item)}>{actionId === item.id ? 'Saving…' : 'Withdraw'}</Button>}</div>)}</div>}</div>
      </Card>}

      {tab !== 'Overview' && tab !== 'Enrollment' && <Card><EmptyState icon="FolderOpen" title={`${tab} — coming into view`} description={`This module will hold ${student.full_name.split(' ')[0]}’s ${tab.toLowerCase()} once its backend workflow is connected.`} /></Card>}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) { return <label className="block"><span className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1.5">{label}</span>{children}</label>; }
function Meta({ icon, label }: { icon: React.ReactNode; label: string }) { return <span className="inline-flex items-center gap-2 text-slate-500 dark:text-slate-400"><span className="text-slate-300 dark:text-slate-600">{icon}</span>{label}</span>; }
function Info({ label, value }: { label: string; value: string }) { return <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-4"><p className="text-xs font-semibold text-slate-400">{label}</p><p className="mt-1 text-slate-700 dark:text-slate-200 break-words">{value}</p></div>; }
function StatBox({ label, value, tone }: { label: string; value: string; tone: string }) { return <Card className="p-4 text-center"><p className={cn('font-display text-2xl font-extrabold', tone)}>{value}</p><p className="text-xs text-slate-400 font-medium mt-0.5">{label}</p></Card>; }
