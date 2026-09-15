import React, { useEffect, useMemo, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  GlobeIcon, CakeIcon, ArrowLeftIcon, SparklesIcon, GraduationCapIcon,
  PlusIcon, XIcon, CheckCircle2Icon, Clock3Icon, XCircleIcon, ShieldCheckIcon,
  FileTextIcon, ImageIcon, DownloadIcon
} from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { Button } from '../components/ui/Button';
import { EmptyState } from '../components/ui/EmptyState';
import { cn } from '../lib/utils';
import {
  createEnrollment, getStudent, listAcademicYears, listClassrooms, listEnrollments,
  listTerms, updateEnrollment, listSubmissions, type ApiAcademicYear,
  type ApiClassroom, type ApiEnrollment, type ApiStudent, type ApiTerm,
  type ApiSubmission
} from '../lib/api';
import { listAttendance, type ApiAttendanceRegister, type AttendanceStatus } from '../lib/attendanceApi';
import { listPortfolioItems, type ApiPortfolioItem } from '../lib/portfolioApi';
import { downloadPublishedAINarrativePdf, listPublishedAINarrativeReports, type PublishedAINarrativeResponse } from '../lib/reportsApi';

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
  const [attendance, setAttendance] = useState<ApiAttendanceRegister[]>([]);
  const [attendanceLoading, setAttendanceLoading] = useState(false);
  const [attendanceError, setAttendanceError] = useState('');
  const [submissions, setSubmissions] = useState<ApiSubmission[]>([]);
  const [assessmentsLoading, setAssessmentsLoading] = useState(false);
  const [assessmentsError, setAssessmentsError] = useState('');
  const [portfolioItems, setPortfolioItems] = useState<ApiPortfolioItem[]>([]);
  const [portfolioLoading, setPortfolioLoading] = useState(false);
  const [portfolioError, setPortfolioError] = useState('');
  const [publishedReports, setPublishedReports] = useState<PublishedAINarrativeResponse[]>([]);
  const [reportsLoading, setReportsLoading] = useState(false);
  const [reportsError, setReportsError] = useState('');

  const loadData = async (studentId: string) => {
    const studentData = await getStudent(studentId);
    const enrollmentData = await listEnrollments({ search: studentData.admission_number });
    setStudent(studentData);
    setEnrollments(enrollmentData.filter((item) => item.student === studentId));
  };

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);
    setError('');
    Promise.resolve()
      .then(() => getStudent(id))
      .then(async (studentData) => {
        const enrollmentData = await listEnrollments({ search: studentData.admission_number });
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

  useEffect(() => {
    if (!id || tab !== 'Attendance') return;
    let cancelled = false;
    setAttendanceLoading(true);
    setAttendanceError('');
    listAttendance({ student: id })
      .then((data) => { if (!cancelled) setAttendance(data); })
      .catch((err) => { if (!cancelled) setAttendanceError(err instanceof Error ? err.message : 'Unable to load attendance.'); })
      .finally(() => { if (!cancelled) setAttendanceLoading(false); });
    return () => { cancelled = true; };
  }, [id, tab]);

  useEffect(() => {
    if (!id || !['Assessments', 'Assignments', 'Teacher Notes'].includes(tab)) return;
    let cancelled = false;
    setAssessmentsLoading(true);
    setAssessmentsError('');
    listSubmissions({ student: id })
      .then((data) => { if (!cancelled) setSubmissions(data); })
      .catch((err) => { if (!cancelled) setAssessmentsError(err instanceof Error ? err.message : 'Unable to load assessment records.'); })
      .finally(() => { if (!cancelled) setAssessmentsLoading(false); });
    return () => { cancelled = true; };
  }, [id, tab]);

  useEffect(() => {
    if (!id || tab !== 'Portfolio') return;
    let cancelled = false;
    setPortfolioLoading(true);
    setPortfolioError('');
    listPortfolioItems({ student: id })
      .then((data) => { if (!cancelled) setPortfolioItems(data); })
      .catch((err) => { if (!cancelled) setPortfolioError(err instanceof Error ? err.message : 'Unable to load portfolio evidence.'); })
      .finally(() => { if (!cancelled) setPortfolioLoading(false); });
    return () => { cancelled = true; };
  }, [id, tab]);

  useEffect(() => {
    if (!id || tab !== 'AI Reports') return;
    let cancelled = false;
    setReportsLoading(true);
    setReportsError('');
    listPublishedAINarrativeReports({ student: id })
      .then((data) => { if (!cancelled) setPublishedReports(data.results); })
      .catch((err) => { if (!cancelled) setReportsError(err instanceof Error ? err.message : 'Unable to load published AI reports.'); })
      .finally(() => { if (!cancelled) setReportsLoading(false); });
    return () => { cancelled = true; };
  }, [id, tab]);

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
      await createEnrollment({ student: id, classroom: form.classroom, academic_year: form.academic_year, term: form.term, enrollment_date: new Date().toISOString().slice(0, 10), status: 'ENROLLED' });
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

  const attendanceStats = useMemo(() => {
    const counts: Record<AttendanceStatus, number> = { PRESENT: 0, LATE: 0, ABSENT: 0, EXCUSED: 0 };
    attendance.forEach((register) => register.records.filter((record) => record.student === id).forEach((record) => { counts[record.status] += 1; }));
    const total = Object.values(counts).reduce((sum, value) => sum + value, 0);
    const attended = counts.PRESENT + counts.LATE;
    return { ...counts, total, rate: total ? Math.round((attended / total) * 100) : null };
  }, [attendance, id]);

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
          <div className="flex sm:flex-col gap-3"><Link to={`/ai-reports?student=${encodeURIComponent(student.id)}`}><Button className="w-full"><SparklesIcon className="h-4 w-4" /> AI Report</Button></Link></div>
        </div>
      </Card>

      <div className="flex gap-1 overflow-x-auto mb-6 rounded-2xl bg-slate-100 dark:bg-slate-800/60 p-1">
        {TABS.map((t) => <button key={t} onClick={() => setTab(t)} className={cn('shrink-0 rounded-xl px-4 py-2 text-sm font-semibold transition-colors', tab === t ? 'bg-white dark:bg-slate-900 text-brand-600 shadow-soft' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300')}>{t}</button>)}
      </div>

      {tab === 'Overview' && <div className="grid grid-cols-1 lg:grid-cols-3 gap-6"><div className="lg:col-span-2 space-y-6"><Card><CardHeader title="Student Information" subtitle="Current database profile" /><div className="grid grid-cols-1 sm:grid-cols-2 gap-4 px-5 pb-5 mt-2 text-sm"><Info label="Email" value={student.email} /><Info label="Gender" value={student.gender} /><Info label="Admission date" value={student.admission_date} /><Info label="Birth certificate" value={student.birth_certificate_number || 'Not provided'} /></div></Card><Card><CardHeader title="Academic placement" subtitle="Enrollment records stored for this learner" /><div className="px-5 pb-5"><Info label="Enrollment records" value={String(enrollments.length)} /><div className="mt-3 text-sm text-slate-500 dark:text-slate-400">{currentEnrollment ? `Currently enrolled in ${currentEnrollment.classroom_name} for ${currentEnrollment.academic_year_name}, Term ${currentEnrollment.term_number}.` : 'No active enrollment is recorded.'}</div></div></Card></div><div className="space-y-6"><Card><CardHeader title="Data available" /><div className="px-5 pb-5 space-y-2 text-sm text-slate-500 dark:text-slate-400"><p>Attendance, assessments, portfolio evidence, teacher notes, and published AI reports are loaded from their own tabs only.</p><p>This keeps the profile fast and avoids downloading unrelated school-wide tables.</p></div></Card></div></div>}

      {tab === 'Enrollment' && <Card>
        <CardHeader title="Enrollment History" subtitle="Academic placement is preserved as historical records" action={<Button type="button" variant="emerald" onClick={openEnrollForm}><PlusIcon className="h-4 w-4" /> Enroll student</Button>} />
        {showEnrollForm && <form onSubmit={submitEnrollment} className="mx-5 mb-5 rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/50"><div className="grid grid-cols-1 md:grid-cols-3 gap-4"><Field label="Academic year"><select value={form.academic_year} onChange={(e) => changeYear(e.target.value)} className={selectClass} disabled={saving}><option value="">Select year</option>{years.map((year) => <option key={year.id} value={year.id}>{year.name}{year.is_current ? ' · Current' : ''}</option>)}</select></Field><Field label="Term"><select value={form.term} onChange={(e) => changeTerm(e.target.value)} className={selectClass} disabled={saving || !form.academic_year}><option value="">Select term</option>{terms.map((term) => <option key={term.id} value={term.id}>Term {term.term_number}{term.is_current ? ' · Current' : ''}</option>)}</select></Field><Field label="Class"><select value={form.classroom} onChange={(e) => setForm({ ...form, classroom: e.target.value })} className={selectClass} disabled={saving || !form.term}><option value="">Select class</option>{classes.map((item) => <option key={item.id} value={item.id}>{item.name}{item.student_count >= item.capacity ? ' · Full' : ''}</option>)}</select></Field></div>{formError && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{formError}</p>}<div className="flex justify-end gap-3 mt-4"><Button type="button" variant="secondary" onClick={() => setShowEnrollForm(false)} disabled={saving}><XIcon className="h-4 w-4" /> Cancel</Button><Button type="submit" variant="emerald" disabled={saving}>{saving ? 'Enrolling…' : 'Confirm enrollment'}</Button></div></form>}
        <div className="px-5 pb-5">{enrollments.length === 0 ? <EmptyState icon="GraduationCap" title="No enrollment history" description="No enrollment records are stored for this student." /> : <div className="divide-y divide-slate-100 dark:divide-slate-800">{enrollments.map((item) => <div key={item.id} className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center"><div className="flex-1 min-w-0"><div className="flex flex-wrap items-center gap-2"><p className="font-semibold text-slate-800 dark:text-slate-100">{item.classroom_name}</p><Badge tone={item.status === 'ENROLLED' ? 'emerald' : 'slate'}>{item.status}</Badge></div><p className="text-sm text-slate-400 mt-1">{item.academic_year_name} · Term {item.term_number} · Enrolled {item.enrollment_date}</p></div>{item.status === 'ENROLLED' && <Button type="button" variant="ghost" className="self-start sm:self-auto" disabled={actionId === item.id} onClick={() => withdrawEnrollment(item)}>{actionId === item.id ? 'Saving…' : 'Withdraw'}</Button>}</div>)}</div>}</div>
      </Card>}

      {tab === 'Attendance' && <Card>
        <CardHeader title="Attendance history" subtitle={attendanceStats.total ? `${attendanceStats.rate}% attendance · ${attendanceStats.total} recorded lessons` : 'Attendance recorded against actual lesson sessions'} />
        {attendanceError && <div className="mx-5 mb-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:bg-rose-950/20 dark:text-rose-300">{attendanceError}</div>}
        {attendanceLoading ? <div className="px-5 py-10 text-center text-sm text-slate-500">Loading attendance…</div> : attendance.length === 0 ? <EmptyState icon="Calendar" title="No attendance records" description="No attendance has been recorded for this student yet." /> : <><div className="grid grid-cols-2 sm:grid-cols-4 gap-3 px-5 pb-5"><MiniStat icon={<CheckCircle2Icon className="h-4 w-4" />} label="Present" value={attendanceStats.PRESENT} /><MiniStat icon={<Clock3Icon className="h-4 w-4" />} label="Late" value={attendanceStats.LATE} /><MiniStat icon={<XCircleIcon className="h-4 w-4" />} label="Absent" value={attendanceStats.ABSENT} /><MiniStat icon={<ShieldCheckIcon className="h-4 w-4" />} label="Excused" value={attendanceStats.EXCUSED} /></div><div className="divide-y divide-slate-100 dark:divide-slate-800">{attendance.map((register) => { const record = register.records.find((item) => item.student === id); if (!record) return null; return <div key={register.id} className="flex items-center gap-4 px-5 py-4"><div className="flex-1"><p className="font-semibold text-sm text-slate-800 dark:text-slate-100">{register.subject_name} · {register.classroom_name}</p><p className="text-xs text-slate-400 mt-1">{new Date(`${register.lesson_date}T00:00:00`).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}</p></div><Badge tone={record.status === 'PRESENT' ? 'emerald' : record.status === 'LATE' ? 'warm' : record.status === 'EXCUSED' ? 'brand' : 'rose'}>{record.status}</Badge></div>; })}</div></>}
      </Card>}

      {['Assessments', 'Assignments'].includes(tab) && <Card>
        <CardHeader title={tab === 'Assessments' ? 'Assessment history' : 'Assignments'} subtitle="Student-specific submissions returned directly by the API" />
        {assessmentsError && <div className="mx-5 mb-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:bg-rose-950/20 dark:text-rose-300">{assessmentsError}</div>}
        {assessmentsLoading ? <div className="px-5 py-10 text-center text-sm text-slate-500">Loading submissions…</div> : submissions.length === 0 ? <EmptyState icon="FileText" title={tab === 'Assessments' ? 'No assessment submissions' : 'No submitted assignments'} description="No records are stored for this student yet." /> : <div className="divide-y divide-slate-100 dark:divide-slate-800">{submissions.map((submission) => <div key={submission.id} className="flex flex-col gap-2 px-5 py-4 sm:flex-row sm:items-center"><div className="flex-1"><p className="font-semibold text-sm text-slate-800 dark:text-slate-100">{submission.assessment_title || `Assessment ${submission.assessment}`}</p><p className="text-xs text-slate-400 mt-1">{submission.assessment_type || 'Assessment'}{submission.assessment_due_date ? ` · Due ${submission.assessment_due_date}` : ''}</p>{submission.teacher_notes && <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">Teacher note: {submission.teacher_notes}</p>}</div><Badge tone={submission.status === 'GRADED' ? 'emerald' : submission.status === 'SUBMITTED' ? 'brand' : 'slate'}>{submission.status}</Badge></div>)}</div>}
      </Card>}

      {tab === 'Behaviour' && <Card><CardHeader title="Behaviour evidence" subtitle="Only stored behaviour records are shown" /><div className="p-5"><EmptyState icon="Heart" title="No behaviour records stored" description="KEY does not currently have a dedicated behaviour-record model, so this tab does not invent or derive behaviour data from unrelated academic records." /></div></Card>}

      {tab === 'Portfolio' && <Card><CardHeader title="Portfolio evidence" subtitle="Learner-specific portfolio items and attached evidence" /><div className="p-5">{portfolioError && <div className="mb-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:bg-rose-950/20 dark:text-rose-300">{portfolioError}</div>}{portfolioLoading ? <div className="py-10 text-center text-sm text-slate-500">Loading portfolio evidence…</div> : portfolioItems.length === 0 ? <EmptyState icon="Image" title="No portfolio evidence" description="No portfolio items are stored for this student." action={<Link to="/portfolio"><Button variant="secondary">Open portfolio</Button></Link>} /> : <div className="grid gap-4 md:grid-cols-2">{portfolioItems.map((item) => <div key={item.id} className="rounded-2xl border border-slate-100 dark:border-slate-800 p-4"><div className="flex items-start justify-between gap-3"><div><p className="font-semibold text-slate-800 dark:text-slate-100">{item.title}</p><p className="text-xs text-slate-400 mt-1">{item.item_type_label} · {item.event_date}</p></div><Badge tone="slate">{item.artifacts.length} evidence</Badge></div>{item.description && <p className="text-sm text-slate-500 dark:text-slate-400 mt-3">{item.description}</p>}{item.assessment_title && <p className="text-xs text-brand-600 mt-3">Linked assessment: {item.assessment_title}</p>}</div>)}</div>}</div></Card>}

      {tab === 'Teacher Notes' && <Card><CardHeader title="Teacher notes" subtitle="Notes attached to this student's assessment submissions" /><div className="p-5">{assessmentsError && <div className="mb-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:bg-rose-950/20 dark:text-rose-300">{assessmentsError}</div>}{assessmentsLoading ? <div className="py-10 text-center text-sm text-slate-500">Loading teacher notes…</div> : submissions.filter((item) => item.teacher_notes?.trim()).length === 0 ? <EmptyState icon="MessageSquare" title="No teacher notes" description="No teacher notes are stored on this student's submissions." /> : <div className="space-y-3">{submissions.filter((item) => item.teacher_notes?.trim()).map((item) => <div key={item.id} className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-4"><p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{item.assessment_title || 'Assessment'}</p><p className="text-sm text-slate-600 dark:text-slate-300 mt-2">{item.teacher_notes}</p></div>)}</div>}</div></Card>}

      {tab === 'AI Reports' && <Card><CardHeader title="Published AI reports" subtitle="Only official teacher-reviewed reports are visible here" /><div className="p-5">{reportsError && <div className="mb-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:bg-rose-950/20 dark:text-rose-300">{reportsError}</div>}{reportsLoading ? <div className="py-10 text-center text-sm text-slate-500">Loading published reports…</div> : publishedReports.length === 0 ? <EmptyState icon="Sparkles" title="No published AI reports" description="Draft and reviewed reports remain in the staff AI Reports workspace until an authorized staff member publishes them." action={<Link to={`/ai-reports?student=${encodeURIComponent(student.id)}`}><Button><SparklesIcon className="h-4 w-4" /> Open AI Reports</Button></Link>} /> : <div className="space-y-4">{publishedReports.map((report) => <div key={report.id} className="rounded-2xl border border-slate-100 dark:border-slate-800 p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="font-semibold text-slate-800 dark:text-slate-100">{report.academic_year_name} · Term {report.term_number}</p><p className="text-xs text-slate-400 mt-1">Published {report.published_at ? new Date(report.published_at).toLocaleString() : '—'}</p></div><Button variant="secondary" onClick={() => downloadPublishedAINarrativePdf(report.id)}><DownloadIcon className="h-4 w-4" /> PDF</Button></div><p className="text-sm text-slate-600 dark:text-slate-300 mt-4 leading-relaxed">{report.narrative.summary}</p></div>)}</div>}</div></Card>}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) { return <label className="block"><span className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1.5">{label}</span>{children}</label>; }
function Meta({ icon, label }: { icon: React.ReactNode; label: string }) { return <span className="inline-flex items-center gap-2 text-slate-500 dark:text-slate-400"><span className="text-slate-300 dark:text-slate-600">{icon}</span>{label}</span>; }
function Info({ label, value }: { label: string; value: string }) { return <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-4"><p className="text-xs font-semibold text-slate-400">{label}</p><p className="mt-1 text-slate-700 dark:text-slate-200 break-words">{value}</p></div>; }
function MiniStat({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) { return <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-3"><div className="flex items-center gap-2 text-slate-400"><span>{icon}</span><span className="text-xs font-semibold">{label}</span></div><p className="mt-1 font-display text-xl font-extrabold text-slate-800 dark:text-white">{value}</p></div>; }
