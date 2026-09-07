import React, { useEffect, useState } from 'react';
import { Loader2Icon, PencilIcon, PrinterIcon, SparklesIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { EmptyState } from '../components/ui/EmptyState';
import { listAcademicYears, listStudents, listTerms, type ApiAcademicYear, type ApiStudent, type ApiTerm } from '../lib/api';
import { generateAINarrativeReport, type AINarrativeResponse } from '../lib/reportsApi';

export function AIReports() {
  const [students, setStudents] = useState<ApiStudent[]>([]);
  const [years, setYears] = useState<ApiAcademicYear[]>([]);
  const [terms, setTerms] = useState<ApiTerm[]>([]);
  const [student, setStudent] = useState('');
  const [year, setYear] = useState('');
  const [term, setTerm] = useState('');
  const [result, setResult] = useState<AINarrativeResponse | null>(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([listStudents({ isActive: true }), listAcademicYears()])
      .then(([studentData, yearData]) => {
        setStudents(studentData);
        setYears(yearData);
        const currentYear = yearData.find((item) => item.is_current)?.id || yearData[0]?.id || '';
        setYear(currentYear);
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load report options.'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!year) { setTerms([]); setTerm(''); return; }
    listTerms({ academicYear: year })
      .then((data) => setTerm((current) => data.some((item) => item.id === current) ? current : (data.find((item) => item.is_current)?.id || data[0]?.id || '')) || setTerms(data))
      .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load terms.'));
  }, [year]);

  const generate = async () => {
    setError('');
    setGenerating(true);
    setResult(null);
    setEditing(false);
    try {
      setResult(await generateAINarrativeReport({ student, academicYear: year, term }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to generate the AI narrative.');
    } finally {
      setGenerating(false);
    }
  };

  const updateNarrative = (key: keyof AINarrativeResponse['narrative'], value: string) => {
    if (!result) return;
    setResult({ ...result, narrative: { ...result.narrative, [key]: value } });
  };

  const selectedStudent = students.find((item) => item.id === student);
  const narrativeSections: Array<[keyof AINarrativeResponse['narrative'], string]> = [
    ['summary', 'Overall Progress'],
    ['strengths', 'Strengths'],
    ['development_areas', 'Areas for Development'],
    ['next_steps', 'Suggested Next Steps'],
    ['teacher_note', 'Teacher Review Note'],
  ];

  return (
    <div>
      <PageHeader
        title="AI Student Reports"
        description="Generate a grounded narrative from the learner's published academic records. Review and refine it before it becomes an official report."
        actions={result ? <>
          <Button variant="secondary" onClick={() => setEditing((value) => !value)}>
            <PencilIcon className="h-4 w-4" /> {editing ? 'Done editing' : 'Edit draft'}
          </Button>
          <Button variant="secondary" onClick={() => window.print()}>
            <PrinterIcon className="h-4 w-4" /> Export PDF
          </Button>
        </> : undefined}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="no-print">
          <Card className="p-5 sticky top-24">
            <h3 className="font-display font-bold text-slate-800 dark:text-slate-100 mb-4">Report Parameters</h3>
            <div className="space-y-4">
              <Field label="Student">
                <select value={student} onChange={(event) => setStudent(event.target.value)} className="w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100">
                  <option value="">Select student</option>
                  {students.map((item) => <option key={item.id} value={item.id}>{item.full_name} — {item.admission_number}</option>)}
                </select>
              </Field>
              <Field label="Academic Year">
                <select value={year} onChange={(event) => setYear(event.target.value)} className="w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100">
                  {years.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
                </select>
              </Field>
              <Field label="Term">
                <select value={term} onChange={(event) => setTerm(event.target.value)} className="w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100">
                  {terms.map((item) => <option key={item.id} value={item.id}>Term {item.term_number}</option>)}
                </select>
              </Field>

              <Button className="w-full" onClick={generate} disabled={loading || generating || !student || !year || !term}>
                {generating ? <Loader2Icon className="h-4 w-4 animate-spin" /> : <SparklesIcon className="h-4 w-4" />}
                {generating ? 'Generating…' : result ? 'Regenerate' : 'Generate AI Report'}
              </Button>
              <p className="text-xs text-slate-400 text-center leading-relaxed">The model receives only the selected learner's report facts. The generated narrative is a draft and requires teacher review.</p>
              {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
            </div>
          </Card>
        </div>

        <div className="lg:col-span-2">
          {!result && !generating && <Card><EmptyState icon="Sparkles" title="Ready when you are" description="Choose a student, academic year, and term, then generate a grounded growth narrative." /></Card>}
          {generating && <Card className="p-10 flex flex-col items-center justify-center text-center"><SparklesIcon className="h-10 w-10 text-emerald-500 animate-pulse mb-4" /><p className="font-display font-bold text-slate-800 dark:text-slate-100">Building the narrative…</p><p className="text-sm text-slate-400 mt-1">Analyzing published assessments, attendance, competencies, and portfolio evidence.</p></Card>}

          {result && <Card className="overflow-hidden print:shadow-none">
            <div className="bg-brand-600 text-white px-7 py-6">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="font-display font-extrabold text-xl">{result.facts.learner.first_name} — Learning Progress Report</p>
                  <p className="text-brand-100 text-sm mt-1">{result.facts.period.academic_year} · Term {result.facts.period.term} · {result.facts.learner.class}</p>
                </div>
                <Badge tone="emerald">AI Draft · Review Required</Badge>
              </div>
            </div>

            <div className="px-7 py-5 border-b border-slate-100 dark:border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-4">
              <Metric label="Assessment Avg" value={result.facts.assessment.average_percentage == null ? '—' : `${result.facts.assessment.average_percentage}%`} />
              <Metric label="Attendance" value={result.facts.attendance.attendance_percentage == null ? '—' : `${result.facts.attendance.attendance_percentage}%`} />
              <Metric label="Published Results" value={String(result.facts.assessment.published_results)} />
              <Metric label="Portfolio Evidence" value={`${result.facts.portfolio.items} / ${result.facts.portfolio.artifacts}`} />
            </div>

            <div className="px-7 py-6 space-y-6">
              {narrativeSections.map(([key, title]) => <section key={key}>
                <h4 className="font-display font-bold text-slate-800 dark:text-slate-100 mb-2">{title}</h4>
                {editing ? <textarea value={result.narrative[key]} onChange={(event) => updateNarrative(key, event.target.value)} rows={4} className="w-full rounded-2xl border border-brand-200 dark:border-slate-700 bg-brand-50/40 dark:bg-slate-800 p-3 text-sm leading-relaxed text-slate-700 dark:text-slate-200" /> : <p className="text-slate-600 dark:text-slate-300 leading-relaxed">{result.narrative[key]}</p>}
              </section>)}
            </div>

            {result.facts.competencies.length > 0 && <div className="px-7 py-5 border-t border-slate-100 dark:border-slate-800">
              <h4 className="font-display font-bold text-slate-800 dark:text-slate-100 mb-3">Competency Evidence Used</h4>
              <div className="flex flex-wrap gap-2">{result.facts.competencies.map((item) => <span key={item.name} className="rounded-full bg-slate-100 dark:bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300">{item.name}: {item.highest_level}</span>)}</div>
            </div>}

            <div className="px-7 py-5 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-400">Generated with {result.model}. This draft is grounded in published KEY records and must be reviewed by an authorized staff member before publication.</div>
          </Card>}
        </div>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div><label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">{label}</label>{children}</div>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-3"><p className="text-xs text-slate-400">{label}</p><p className="mt-1 font-display font-extrabold text-lg text-slate-800 dark:text-slate-100">{value}</p></div>;
}
