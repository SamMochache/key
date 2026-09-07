import React, { useEffect, useState } from 'react';
import { ArrowRightIcon, BarChart3, CalendarCheck, DownloadIcon, GraduationCap, School, Sparkles, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { cn } from '../lib/utils';
import { listAcademicYears, listStudents, listTerms, type ApiAcademicYear, type ApiStudent, type ApiTerm } from '../lib/api';
import { downloadStudentReport } from '../lib/reportsApi';
import { useApp } from '../context/AppContext';

const reports = [
  { title: 'Attendance Report', desc: 'Presence rates by class, month, and student.', icon: CalendarCheck, tone: 'brand', to: '/analytics' },
  { title: 'Class Report', desc: 'A snapshot of each learning community.', icon: School, tone: 'emerald', to: '/classes' },
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
  const [years, setYears] = useState<ApiAcademicYear[]>([]);
  const [terms, setTerms] = useState<ApiTerm[]>([]);
  const [student, setStudent] = useState('');
  const [year, setYear] = useState('');
  const [term, setTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [reportError, setReportError] = useState('');

  useEffect(() => {
    if (role === 'student') {
      setLoading(false);
      return;
    }
    Promise.all([listStudents({ isActive: true }), listAcademicYears()])
      .then(([studentData, yearData]) => {
        setStudents(studentData);
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

  const generateStudentReport = async () => {
    setReportError('');
    setGenerating(true);
    try {
      await downloadStudentReport({ student, academicYear: year || undefined, term: term || undefined });
    } catch (err) {
      setReportError(err instanceof Error ? err.message : 'Unable to generate the report.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div>
      <PageHeader title="Reports" description="Generate beautiful, printable reports for families, staff, and leadership." />

      <div id="student-report" className="mb-8">
        <Card className="p-5">
          <div className="flex flex-col gap-1 mb-5">
            <h2 className="font-display font-bold text-lg text-slate-800 dark:text-slate-100">Student Progress Report</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Generate a PDF from published academic records for a selected term.</p>
          </div>

          {role === 'student' ? (
            <div className="rounded-xl bg-slate-50 dark:bg-slate-800/60 px-4 py-3 text-sm text-slate-600 dark:text-slate-300">
              Your report is generated from your own published records. Use the button below to download it.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                Student
                <select value={student} onChange={(event) => setStudent(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100">
                  <option value="">Select student</option>
                  {students.map((item) => <option key={item.id} value={item.id}>{item.full_name} — {item.admission_number}</option>)}
                </select>
              </label>
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                Academic Year
                <select value={year} onChange={(event) => setYear(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100">
                  <option value="">Any available year</option>
                  {years.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
                </select>
              </label>
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                Term
                <select value={term} onChange={(event) => setTerm(event.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100">
                  <option value="">Any term</option>
                  {terms.map((item) => <option key={item.id} value={item.id}>Term {item.term_number}</option>)}
                </select>
              </label>
            </div>
          )}

          {(error || reportError) && <p className="mt-4 text-sm text-red-600 dark:text-red-400">{reportError || error}</p>}
          <div className="mt-5 flex justify-end">
            <button
              type="button"
              disabled={loading || generating || (role !== 'student' && !student)}
              onClick={generateStudentReport}
              className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <DownloadIcon className="h-4 w-4" />
              {generating ? 'Generating…' : 'Generate PDF'}
            </button>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.filter((report) => report.title !== 'Student Progress Report').map((r) => {
          const Icon = r.icon;
          return (
            <Card key={r.title} className="p-5 flex flex-col hover:-translate-y-0.5 transition-transform">
              <span className={cn('flex h-12 w-12 items-center justify-center rounded-2xl mb-4', tone[r.tone])}><Icon className="h-5 w-5" /></span>
              <h3 className="font-display font-bold text-slate-800 dark:text-slate-100">{r.title}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 flex-1">{r.desc}</p>
              <div className="flex items-center gap-2 mt-4">
                <Link to={r.to} className="inline-flex items-center gap-1.5 text-sm font-bold text-brand-600 hover:gap-2 transition-all">Open <ArrowRightIcon className="h-4 w-4" /></Link>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
