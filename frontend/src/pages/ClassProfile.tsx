import React, { useEffect, useState } from 'react';
import { ArrowLeftIcon, BookOpenIcon, GraduationCapIcon, PlusIcon, UsersIcon, XIcon } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Card, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import { cn } from '../lib/utils';
import { createEnrollment, getClassroom, listAcademicYears, listEnrollments, listStudents, listTerms, type ApiAcademicYear, type ApiClassroom, type ApiEnrollment, type ApiStageSubject, type ApiStudent, type ApiTerm, listStageSubjects } from '../lib/api';

export function ClassProfile() {
  const { id } = useParams();
  const [classroom, setClassroom] = useState<ApiClassroom | null>(null);
  const [enrollments, setEnrollments] = useState<ApiEnrollment[]>([]);
  const [subjects, setSubjects] = useState<ApiStageSubject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showEnrollForm, setShowEnrollForm] = useState(false);
  const [students, setStudents] = useState<ApiStudent[]>([]);
  const [academicYears, setAcademicYears] = useState<ApiAcademicYear[]>([]);
  const [terms, setTerms] = useState<ApiTerm[]>([]);
  const [form, setForm] = useState({ student: '', academic_year: '', term: '' });
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  const loadClass = async () => {
    if (!id) return;
    setLoading(true);
    setError('');
    try {
      const classData = await getClassroom(id);
      const [enrollmentData, subjectData] = await Promise.all([
        listEnrollments({ classroom: id, status: 'ENROLLED' }),
        classData.cambridge_stage ? listStageSubjects({ stage: classData.cambridge_stage, active: true }) : Promise.resolve([]),
      ]);
      setClassroom(classData);
      setEnrollments(enrollmentData);
      setSubjects(subjectData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load class.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;
    if (!id) return;
    Promise.all([getClassroom(id), listEnrollments({ classroom: id, status: 'ENROLLED' })])
      .then(async ([classData, enrollmentData]) => {
        const subjectData = classData.cambridge_stage ? await listStageSubjects({ stage: classData.cambridge_stage, active: true }) : [];
        if (!cancelled) { setClassroom(classData); setEnrollments(enrollmentData); setSubjects(subjectData); }
      })
      .catch((err) => { if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load class.'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [id]);

  const openEnrollmentForm = async () => {
    if (!classroom) return;
    setFormError('');
    setShowEnrollForm(true);
    if (students.length || academicYears.length) return;
    try {
      const [studentData, yearData] = await Promise.all([
        listStudents({ isActive: true }),
        listAcademicYears(),
      ]);
      setStudents(studentData);
      setAcademicYears(yearData);
      const currentYear = yearData.find((year) => year.id === classroom.academic_year) || yearData.find((year) => year.is_current);
      if (currentYear) {
        setForm((current) => ({ ...current, academic_year: currentYear.id }));
        const termData = await listTerms({ academicYear: currentYear.id });
        setTerms(termData);
        setForm((current) => ({ ...current, term: termData.find((term) => term.id === classroom.term)?.id || termData.find((term) => term.is_current)?.id || '' }));
      }
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unable to load enrollment options.');
    }
  };

  const changeAcademicYear = async (academicYear: string) => {
    setForm((current) => ({ ...current, academic_year: academicYear, term: '' }));
    try {
      setTerms(await listTerms({ academicYear }));
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unable to load terms.');
    }
  };

  const submitEnrollment = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!id || !classroom) return;
    setFormError('');
    if (!form.student || !form.academic_year || !form.term) { setFormError('Select a student, academic year, and term.'); return; }
    if (classroom.capacity && classroom.student_count >= classroom.capacity) { setFormError('This classroom has reached its capacity.'); return; }
    if (enrollments.some((enrollment) => enrollment.student === form.student)) { setFormError('This student is already enrolled in this classroom.'); return; }
    setSaving(true);
    try {
      await createEnrollment({ student: form.student, classroom: id, academic_year: form.academic_year, term: form.term, enrollment_date: new Date().toISOString().slice(0, 10) });
      setShowEnrollForm(false);
      setForm({ student: '', academic_year: classroom.academic_year, term: classroom.term });
      await loadClass();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unable to enroll student.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Card className="p-8 text-center text-sm text-slate-500">Loading class…</Card>;
  if (!classroom) return <Card><EmptyState icon="School" title="Class not found" description={error || 'This class is not available to your account.'} action={<Link to="/classes"><Button>Back to classes</Button></Link>} /></Card>;

  const occupancy = classroom.capacity ? Math.round((classroom.student_count / classroom.capacity) * 100) : 0;
  const enrolledIds = new Set(enrollments.map((enrollment) => enrollment.student));
  const availableStudents = students.filter((student) => !enrolledIds.has(student.id));

  return (
    <div>
      <Link to="/classes" className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-400 hover:text-brand-600 mb-4"><ArrowLeftIcon className="h-4 w-4" /> All classes</Link>
      <PageHeader title={classroom.name} description={`${classroom.stage_name} · ${classroom.academic_year_name} · Term ${classroom.term_number}`} />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatBox label="Students" value={classroom.student_count} icon={<UsersIcon className="h-4 w-4" />} />
        <StatBox label="Capacity" value={classroom.capacity} icon={<GraduationCapIcon className="h-4 w-4" />} />
        <StatBox label="Subjects" value={subjects.length} icon={<BookOpenIcon className="h-4 w-4" />} />
        <StatBox label="Occupancy" value={`${occupancy}%`} />
      </div>

      {showEnrollForm && (
        <Card className="mb-6">
          <CardHeader title="Enroll Student" subtitle={`Add a student to ${classroom.name}`} action={<Button variant="ghost" type="button" onClick={() => setShowEnrollForm(false)} aria-label="Close enrollment form"><XIcon className="h-4 w-4" /></Button>} />
          <form onSubmit={submitEnrollment} className="px-5 pb-5 pt-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Field label="Student">
                <select value={form.student} onChange={(event) => setForm({ ...form, student: event.target.value })} className={selectClass} disabled={saving}>
                  <option value="">Select student</option>
                  {availableStudents.map((student) => <option key={student.id} value={student.id}>{student.full_name} · {student.admission_number}</option>)}
                </select>
              </Field>
              <Field label="Academic year">
                <select value={form.academic_year} onChange={(event) => changeAcademicYear(event.target.value)} className={selectClass} disabled={saving}>
                  <option value="">Select year</option>
                  {academicYears.map((year) => <option key={year.id} value={year.id}>{year.name}{year.is_current ? ' · Current' : ''}</option>)}
                </select>
              </Field>
              <Field label="Term">
                <select value={form.term} onChange={(event) => setForm({ ...form, term: event.target.value })} className={selectClass} disabled={saving || !form.academic_year}>
                  <option value="">Select term</option>
                  {terms.map((term) => <option key={term.id} value={term.id}>Term {term.term_number}{term.is_current ? ' · Current' : ''}</option>)}
                </select>
              </Field>
            </div>
            {formError && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{formError}</p>}
            <div className="flex justify-end gap-3 mt-5"><Button type="button" variant="secondary" onClick={() => setShowEnrollForm(false)} disabled={saving}>Cancel</Button><Button type="submit" variant="emerald" disabled={saving || availableStudents.length === 0}>{saving ? 'Enrolling…' : 'Enroll student'}</Button></div>
          </form>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader title="Enrolled Students" subtitle={`${enrollments.length} active students in this class`} action={!showEnrollForm ? <Button type="button" variant="emerald" onClick={openEnrollmentForm} disabled={!!classroom.capacity && classroom.student_count >= classroom.capacity}><PlusIcon className="h-4 w-4" /> Enroll student</Button> : undefined} />
          <div className="px-5 pb-5 mt-3">
            {enrollments.length === 0 ? <EmptyState icon="Users" title="No enrolled students" description="Students will appear here once they are enrolled in this classroom." /> : <div className="divide-y divide-slate-100 dark:divide-slate-800">{enrollments.map((enrollment) => <Link key={enrollment.id} to={`/students/${enrollment.student}`} className="flex items-center gap-3 py-3 first:pt-1 hover:bg-slate-50 dark:hover:bg-slate-800/40 rounded-xl px-2 transition-colors"><Avatar name={enrollment.student_name} size={40} /><div className="min-w-0 flex-1"><p className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">{enrollment.student_name}</p><p className="text-xs text-slate-400">{enrollment.admission_number} · Enrolled {enrollment.enrollment_date}</p></div><Badge tone="emerald">Enrolled</Badge></Link>)}</div>}
          </div>
        </Card>
        <Card><CardHeader title="Subjects" subtitle="Active stage subjects" /><div className="px-5 pb-5 mt-3 space-y-2">{subjects.length === 0 ? <EmptyState icon="BookOpen" title="No subjects assigned" /> : subjects.map((subject) => <div key={subject.id} className="flex items-center justify-between gap-3 rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-3"><div className="min-w-0"><p className="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">{subject.subject_name}</p><p className="text-xs text-slate-400">{subject.weekly_lessons} lessons/week</p></div><Badge tone={subject.is_core ? 'emerald' : 'slate'}>{subject.is_core ? 'Core' : 'Elective'}</Badge></div>)}</div></Card>
      </div>
    </div>
  );
}

const selectClass = 'w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-sm text-slate-700 dark:text-slate-200 outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10';
function Field({ label, children }: { label: string; children: React.ReactNode }) { return <label className="block"><span className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1.5">{label}</span>{children}</label>; }
function StatBox({ label, value, icon }: { label: string; value: string | number; icon?: React.ReactNode }) { return <Card className="p-4"><div className="flex items-center justify-center gap-1.5 text-slate-400 text-xs font-semibold">{icon}{label}</div><p className={cn('font-display text-2xl font-extrabold text-center mt-1 text-slate-800 dark:text-slate-100')}>{value}</p></Card>; }
