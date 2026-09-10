import React, { useEffect, useState } from 'react';
import { DownloadIcon, FileTextIcon, Loader2Icon, SparklesIcon, UserRoundIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';
import { Button } from '../components/ui/Button';
import {
  listPublishedAINarrativeReports,
  downloadPublishedAINarrativePdf,
  downloadStudentReport,
  type PublishedAINarrativeResponse,
} from '../lib/reportsApi';
import { listMyChildren, type ParentChild } from '../lib/parentApi';

export function ParentAIReports() {
  const [reports, setReports] = useState<PublishedAINarrativeResponse[]>([]);
  const [children, setChildren] = useState<ParentChild[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([listPublishedAINarrativeReports(), listMyChildren()])
      .then(([reportData, linkedChildren]) => {
        setReports(reportData.results);
        setChildren(linkedChildren);
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load learner reports.'))
      .finally(() => setLoading(false));
  }, []);

  const downloadAI = async (id: string) => {
    setDownloading(`ai:${id}`);
    setError('');
    try {
      await downloadPublishedAINarrativePdf(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to download the AI narrative report.');
    } finally {
      setDownloading('');
    }
  };

  const downloadProgress = async (studentId: string) => {
    setDownloading(`progress:${studentId}`);
    setError('');
    try {
      await downloadStudentReport({ student: studentId });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to download the student progress report.');
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

      {loading && <Card className="p-10 flex flex-col items-center justify-center text-center"><Loader2Icon className="h-8 w-8 animate-spin text-brand-600 mb-4" /><p className="font-display font-bold text-slate-800 dark:text-slate-100">Loading learner reports…</p></Card>}

      {!loading && children.length > 0 && (
        <Card className="mb-6 overflow-hidden">
          <div className="px-6 py-5 border-b border-slate-100 dark:border-slate-800">
            <h2 className="font-display font-extrabold text-lg text-slate-900 dark:text-white">Student Progress Reports</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Download the latest academic progress report for each learner you are authorized to access.</p>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {children.filter((child) => child.can_view_reports).map((child) => (
              <div key={child.id} className="px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-2xl bg-brand-50 dark:bg-brand-500/10 flex items-center justify-center"><UserRoundIcon className="h-5 w-5 text-brand-600" /></div>
                  <div>
                    <p className="font-display font-bold text-slate-800 dark:text-slate-100">{child.full_name}</p>
                    <p className="text-xs text-slate-400 mt-1">{child.admission_number} · {child.classroom?.name || 'Not currently enrolled'}</p>
                  </div>
                </div>
                <Button variant="secondary" onClick={() => downloadProgress(child.id)} disabled={downloading === `progress:${child.id}`}>
                  {downloading === `progress:${child.id}` ? <Loader2Icon className="h-4 w-4 animate-spin" /> : <DownloadIcon className="h-4 w-4" />}
                  {downloading === `progress:${child.id}` ? 'Preparing…' : 'Download progress PDF'}
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {!loading && reports.length === 0 && (
        <Card>
          <EmptyState
            icon="FileText"
            title="No published AI narrative reports yet"
            description={children.length > 0
              ? 'Your linked learners are available above. AI narrative reports will appear here after the school reviews and publishes them.'
              : 'No linked learners or published reports are available for this parent account.'}
          />
        </Card>
      )}

      {!loading && reports.length > 0 && <div className="space-y-5">
        {reports.map((report) => (
          <Card key={report.id} className="overflow-hidden">
            <div className="bg-brand-600 text-white px-6 py-5 flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="font-display font-extrabold text-xl">{report.student_name}</p>
                <p className="text-brand-100 text-sm mt-1">AI Learning Progress Report · {report.academic_year_name} · Term {report.term_number}</p>
              </div>
              <Button variant="secondary" onClick={() => downloadAI(report.id)} disabled={downloading === `ai:${report.id}`}>
                {downloading === `ai:${report.id}` ? <Loader2Icon className="h-4 w-4 animate-spin" /> : <DownloadIcon className="h-4 w-4" />}
                {downloading === `ai:${report.id}` ? 'Preparing…' : 'Download AI PDF'}
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
