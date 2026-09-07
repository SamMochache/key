import React, { useEffect, useState } from 'react';
import { DownloadIcon, FileTextIcon, Loader2Icon, SparklesIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';
import { Button } from '../components/ui/Button';
import { listPublishedAINarrativeReports, downloadPublishedAINarrativePdf, type PublishedAINarrativeResponse } from '../lib/reportsApi';

export function ParentAIReports() {
  const [reports, setReports] = useState<PublishedAINarrativeResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    listPublishedAINarrativeReports()
      .then((data) => setReports(data.results))
      .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load published reports.'))
      .finally(() => setLoading(false));
  }, []);

  const download = async (id: string) => {
    setDownloading(id);
    setError('');
    try {
      await downloadPublishedAINarrativePdf(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to download the report.');
    } finally {
      setDownloading('');
    }
  };

  return (
    <div>
      <PageHeader
        title="Learner Reports"
        description="View published learning progress reports for the students linked to your parent account."
      />

      {error && <Card className="mb-5 p-4 border-rose-200 dark:border-rose-900"><p className="text-sm text-rose-600 dark:text-rose-400">{error}</p></Card>}

      {loading && <Card className="p-10 flex flex-col items-center justify-center text-center"><Loader2Icon className="h-8 w-8 animate-spin text-brand-600 mb-4" /><p className="font-display font-bold text-slate-800 dark:text-slate-100">Loading published reports…</p></Card>}

      {!loading && reports.length === 0 && <Card><EmptyState icon="FileText" title="No published reports yet" description="The school will publish a learner report after it has been reviewed by an authorized staff member." /></Card>}

      {!loading && reports.length > 0 && <div className="space-y-5">
        {reports.map((report) => (
          <Card key={report.id} className="overflow-hidden">
            <div className="bg-brand-600 text-white px-6 py-5 flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="font-display font-extrabold text-xl">{report.student_name}</p>
                <p className="text-brand-100 text-sm mt-1">Learning Progress Report · {report.academic_year_name} · Term {report.term_number}</p>
              </div>
              <Button variant="secondary" onClick={() => download(report.id)} disabled={downloading === report.id}>
                {downloading === report.id ? <Loader2Icon className="h-4 w-4 animate-spin" /> : <DownloadIcon className="h-4 w-4" />}
                {downloading === report.id ? 'Preparing…' : 'Download PDF'}
              </Button>
            </div>

            <div className="px-6 py-5 grid grid-cols-2 sm:grid-cols-4 gap-3 border-b border-slate-100 dark:border-slate-800">
              <Metric label="Assessment Avg" value={report.facts.assessment.average_percentage == null ? '—' : `${report.facts.assessment.average_percentage}%`} />
              <Metric label="Attendance" value={report.facts.attendance.attendance_percentage == null ? '—' : `${report.facts.attendance.attendance_percentage}%`} />
              <Metric label="Results" value={String(report.facts.assessment.published_results)} />
              <Metric label="Evidence" value={`${report.facts.portfolio.items} / ${report.facts.portfolio.artifacts}`} />
            </div>

            <div className="px-6 py-6 space-y-6">
              <Section title="Overall Progress" text={report.narrative.summary} />
              <Section title="Strengths" text={report.narrative.strengths} />
              <Section title="Areas for Development" text={report.narrative.development_areas} />
              <Section title="Suggested Next Steps" text={report.narrative.next_steps} />
              <Section title="Teacher Review Note" text={report.narrative.teacher_note} />
            </div>

            {report.facts.competencies.length > 0 && <div className="px-6 py-5 border-t border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 mb-3"><SparklesIcon className="h-4 w-4 text-brand-600" /><h3 className="font-display font-bold text-slate-800 dark:text-slate-100">Competency Evidence</h3></div>
              <div className="flex flex-wrap gap-2">{report.facts.competencies.map((item) => <span key={item.name} className="rounded-full bg-slate-100 dark:bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300">{item.name}: {item.highest_level}</span>)}</div>
            </div>}

            <div className="px-6 py-4 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-400 flex items-center gap-2"><FileTextIcon className="h-4 w-4" /> Published {report.published_at ? new Date(report.published_at).toLocaleString() : 'report'}. This is the official reviewed version.</div>
          </Card>
        ))}
      </div>}
    </div>
  );
}

function Section({ title, text }: { title: string; text: string }) {
  return <section><h3 className="font-display font-bold text-slate-800 dark:text-slate-100 mb-2">{title}</h3><p className="text-slate-600 dark:text-slate-300 leading-relaxed">{text}</p></section>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-3"><p className="text-xs text-slate-400">{label}</p><p className="mt-1 font-display font-extrabold text-lg text-slate-800 dark:text-slate-100">{value}</p></div>;
}
