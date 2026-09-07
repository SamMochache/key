import React, { useEffect, useState } from 'react';
import { ArrowRightIcon, BarChart3, CalendarCheck, DownloadIcon, GraduationCap, School, Sparkles, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { cn } from '../lib/utils';
import { listAcademicYears, listClassrooms, listStudents, listTerms, type ApiAcademicYear, type ApiClassroom, type ApiStudent, type ApiTerm } from '../lib/api';
import { downloadAttendanceReport, downloadClassReport, downloadStudentReport } from '../lib/reportsApi';
import { useApp } from '../context/AppContext';

const reports = [
  { title: 'Attendance Report', desc: 'Presence rates by class, month, and student.', icon: CalendarCheck, tone: 'brand', to: '#attendance-report' },
  { title: 'Class Report', desc: 'A printable academic snapshot of each learning community.', icon: School, tone: 'emerald', to: '#class-report' },
  { title: 'Student Progress Report', desc: 'Published assessment, attendance, and competency outcomes.', icon: TrendingUp, tone: 'warm', to: '#student-report' },
  { title: 'AI Narrative Report', desc: 'Warm, growth-focused stories per child.', icon: Sparkles, tone: 'emerald', to: '/ai-reports' },
  { title: 'Performance Analytics', desc: 'Outcomes, trends, and comparisons.', icon: BarChart3, tone: 'brand', to: '/analytics' },
  { title: 'Teacher Report', desc: 'Workload, observations, and grading.', icon: GraduationCap, tone: 'warm', to: '/classes' },
];

const tone: Record<string, string> = {
  brand: 'bg-brand-50 text-brand-600 dark:bg-brand-600/20 dark:text-brand-300',
  emerald: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-300',
  warm: 'bg-warm-50 text-warm-600 dark:bg-warm-500/20 dark:text-warm-300',
};

export function Reports() {
  const { role } = useApp();
  const [students, setStudents] = useState<ApiStudent[]>([]);
  const [classrooms, setClassrooms] = useState<ApiClassroom[]>([]);
  const [years, setYears] = useState<ApiAcademicYear[]>([]);
  const [terms, setTerms] = useState<ApiTerm[]>([]);
  const [student, setStudent] = useState('');
  const [classroom, setClassroom] = useState('');
  const [attendanceStudent, setAttendanceStudent] = useState('');
  const [attendanceClassroom, setAttendanceClassroom] = useState('');
  const [year, setYear] = useState('');
  const [term, setTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [generatingStudent, setGeneratingStudent] = useState(false);
  const [generatingClass, setGeneratingClass] = useState(false);
  const [generatingAttendance, setGeneratingAttendance] = useState(false);
  const [error, setError] = useState('');
  const [reportError, setReportError] = useState('');

  useEffect(() => {
    if (role === 'student') {
      setLoading(false);
      return;
    }
    Promise.all([
      listStudents({ isActive: true }),
      listClassrooms({ active: true }),
      listAcademicYears(),
    ])
      .then(([studentData, classroomData, yearData]) => {
        setStudents(studentData);
        setClassrooms(classroomData);
        setYears(yearData);
        if (yearData.length) setYear(yearData.find((item) => item.is_current)?.id || yearData[0].id);
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load report options.'))
      .finally(() => setLoading(false));
  }, [role]);

  useEffect(() => {
    if (!year) {
      setTerms([]);
      setTerm('');
      return;
    }
    listTerms({ academicYear: year })
      .then((data) => {
        setTerms(data);
        setTerm((current) => data.some((item) => item.id === current) ? current : (data.find((item) => item.is_current)?.id || data[0]?.id || ''));
      })
      .catch((err) => setReportError(err instanceof Error ? err.message : 'Unable to load terms.'));
  }, [year]);

  useEffect(() => {
    if (role === 'student' || !year) return;
    listClassrooms({ academicYear: year, active: true })
      .then((data) => {
        setClassrooms(data);
        setClassroom((current) => data.some((item) => item.id === current) ? current : '');
        setAttendanceClassroom((current) => data.some((item) => item.id === current) ? current : '');
      })
      .catch((err) => setReportError(err instanceof Error ? err.message : 'Unable to load classes.'));
  }, [year, role]);

  const generateStudentReport = async () => {
    setReportError('');
    setGeneratingStudent(true);
    try {
      await downloadStudentReport({ student: role === 'student' ? '' : student, academicYear: year || undefined, term: term || undefined });
    } catch (err) {
      setReportError(err instanceof Error ? err.message : 'Unable to generate the report.');
    } finally {
      setGeneratingStudent(false);
    }
  };

  const generateClassReport = async () => {
    setReportError('');
    setGeneratingClass(true);
    try {
      await downloadClassReport({ classroom, academicYear: year || undefined, term: term || undefined });
    } catch (err) {
      setReportError(err instanceof Error ? err.message : 'Unable to generate the class report.');
    } finally {
      setGeneratingClass(false);
    }
  };

  const generateAttendanceReport = async () => {
    setReportError('');
    setGeneratingAttendance(true);
    try {
      await downloadAttendanceReport({
        classroom: attendanceClassroom || undefined,
        student: attendanceStudent || undefined,
        academicYear: year || undefined,
        term: term || undefined,
      });
    } catch (err) {
      setReportError(err instanceof Error ? err.message : 'Unable to generate the attendance report.');
    } finally {
      setGeneratingAttendance(false);
    }
  };

  return (
    <div>
      <PageHeader title="Reports" description="Generate beautiful, printable reports for families, staff, and leadership." />

      <div id="attendance-report" className="mb-8">
        <Card className="p-5">
          <div className="flex flex-col gap-1 mb-5">
            <h2 className="font-display font-bold text-lg text-slate-800 dark:text-slate-100">Attendance Summary Report</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Generate attendance totals and rates for a class or individual learner.</p>
          </div>
          {role === 'student' ? (
            <div className="rounded-xl bg-slate-50 dark:bg-slate-800/60 px-4 py-3 text-sm text-slate-600 dark:text-slate-300">Attendance reports are available to staff. Your attendance is included in your Student Progress Report.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Class
                <select value={attendanceClassroom} onChange={(event) => { setAttendanceClassroom(event.target.value); setAttendanceStudent(''); }} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100">
                  <option value="">All classes</option>
                  {classrooms.map((item) => <option key={item.id} value={item.id}>{item.name} — {item.code}</option>)}
                </select>
              </label>
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Student (optional)
                <select value={attendanceStudent} onChange={(event) => setAttendanceStudent(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100">
                  <option value="">All students</option>
                  {students.map((item) => <option key={item.id} value={item.id}>{item.full_name} — {item.admission_number}</option>)}
                </select>
              </label>
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Academic Year
                <select value={year} onChange={(event) => setYear(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-900 dark:bg-slate-900 dark:text-slate-100">
                  <option value="">Any available year</option>
                  {years.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
                </select>
              </label>
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Term
                <select value={term} onChange={(event) => setTerm(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100">
                  <option value="">Any term</option>
                  {terms.map((item) => <option key={item.id} value={item.id}>Term {item.term_number}</option>)}
                </select>
              </label>
            </div>
          )}
          {(error || reportError) && <p className="mt-4 text-sm text-red-600 dark:text-red-400">{reportError || error}</p>}
          {role !== 'student' && <div className="mt-5 flex justify-end"><button type="button" disabled={loading || generatingAttendance || (!attendanceClassroom && !attendanceStudent)} onClick={generateAttendanceReport} className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"><DownloadIcon className="h-4 w-4" />{generatingAttendance ? 'Generating…' : 'Generate Attendance PDF'}</button></div>}
        </Card>
      </div>

      <div id="student-report" className="mb-8">
        <Card className="p-5">
          <div className="flex flex-col gap-1 mb-5"><h2 className="font-display font-bold text-lg text-slate-800 dark:text-slate-100">Student Progress Report</h2><p className="text-sm text-slate-500 dark:text-slate-400">Generate a PDF from published academic records for a selected term.</p></div>
          {role === 'student' ? <div className="rounded-xl bg-slate-50 dark:bg-slate-800/60 px-4 py-3 text-sm text-slate-600 dark:text-slate-300">Your report is generated from your own published records. Use the button below to download it.</div> : <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Student<select value={student} onChange={(event) => setStudent(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"><option value="">Select student</option>{students.map((item) => <option key={item.id} value={item.id}>{item.full_name} — {item.admission_number}</option>)}</select></label>
            <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Academic Year<select value={year} onChange={(event) => setYear(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"><option value="">Any available year</option>{years.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Term<select value={term} onChange={(event) => setTerm(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"><option value="">Any term</option>{terms.map((item) => <option key={item.id} value={item.id}>Term {item.term_number}</option>)}</select></label>
          </div>}
          {(error || reportError) && <p className="mt-4 text-sm text-red-600 dark:text-red-400">{reportError || error}</p>}
          <div className="mt-5 flex justify-end"><button type="button" disabled={loading || generatingStudent || (role !== 'student' && !student)} onClick={generateStudentReport} className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"><DownloadIcon className="h-4 w-4" />{generatingStudent ? 'Generating…' : 'Generate PDF'}</button></div>
        </Card>
      </div>

      {role !== 'student' && <div id="class-report" className="mb-8"><Card className="p-5"><div className="flex flex-col gap-1 mb-5"><h2 className="font-display font-bold text-lg text-slate-800 dark:text-slate-100">Class Report</h2><p className="text-sm text-slate-500 dark:text-slate-400">Generate a printable class snapshot with learner performance and attendance.</p></div><div className="grid grid-cols-1 md:grid-cols-3 gap-4"><label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Class<select value={classroom} onChange={(event) => setClassroom(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"><option value="">Select class</option>{classrooms.map((item) => <option key={item.id} value={item.id}>{item.name} — {item.code}</option>)}</select></label><label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Academic Year<select value={year} onChange={(event) => setYear(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"><option value="">Select year</option>{years.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Term<select value={term} onChange={(event) => setTerm(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"><option value="">Select term</option>{terms.map((item) => <option key={item.id} value={item.id}>Term {item.term_number}</option>)}</select></label></div><div className="mt-5 flex justify-end"><button type="button" disabled={loading || generatingClass || !classroom} onClick={generateClassReport} className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"><DownloadIcon className="h-4 w-4" />{generatingClass ? 'Generating…' : 'Generate Class PDF'}</button></div></Card></div>}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">{reports.filter((report) => report.title !== 'Student Progress Report' && report.title !== 'Class Report' && report.title !== 'Attendance Report').map((r) => { const Icon = r.icon; return <Card key={r.title} className="p-5 flex flex-col hover:-translate-y-0.5 transition-transform"><span className={cn('flex h-12 w-12 items-center justify-center rounded-2xl mb-4', tone[r.tone])}><Icon className="h-5 w-5" /></span><h3 className="font-display font-bold text-slate-800 dark:text-slate-100">{r.title}</h3><p className="text-sm text-slate-500 dark:text-slate-400 mt-1 flex-1">{r.desc}</p><div className="flex items-center gap-2 mt-4"><Link to={r.to} className="inline-flex items-center gap-1.5 text-sm font-bold text-brand-600 hover:gap-2 transition-all">Open <ArrowRightIcon className="h-4 w-4" /></Link></div></Card>; })}</div>
    </div>
  );
}
