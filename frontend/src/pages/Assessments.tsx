import React, { useEffect, useMemo, useState } from 'react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card, CardHeader } from '../components/ui/Card';
import { StatCard } from '../components/ui/StatCard';
import { Badge } from '../components/ui/Badge';
import { CompetencyRadarChart } from '../components/charts/Charts';
import { assignments as fallbackAssignments } from '../lib/data';
import {
  getAccessToken,
  getDashboardSummary,
  listAssessments,
  listSubmissions,
  type ApiAssessment,
  type ApiSubmission,
  type DashboardSummary
} from '../lib/api';

const outcomes = [
  { label: 'Emerging', pct: 18, tone: 'bg-warm-500' },
  { label: 'Developing', pct: 34, tone: 'bg-brand-500' },
  { label: 'Secure', pct: 32, tone: 'bg-emerald-500' },
  { label: 'Mastered', pct: 16, tone: 'bg-emerald-600' }
];

function formatDueDate(value: string | null) {
  if (!value) return 'No due date';
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' }).format(
    new Date(`${value}T00:00:00`)
  );
}

function apiStatus(status: string) {
  const normalized = status.toLowerCase();
  if (normalized.includes('published') || normalized.includes('complete')) return 'Grading';
  if (normalized.includes('closed')) return 'Closed';
  return 'Open';
}

export function Assessments() {
  const [remoteAssessments, setRemoteAssessments] = useState<ApiAssessment[] | null>(null);
  const [remoteSubmissions, setRemoteSubmissions] = useState<ApiSubmission[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);

  useEffect(() => {
    let active = true;
    const token = getAccessToken();

    if (!token) return () => { active = false; };

    Promise.all([listAssessments(), listSubmissions(), getDashboardSummary()])
      .then(([assessments, submissions, dashboardSummary]) => {
        if (!active) return;
        setRemoteAssessments(assessments);
        setRemoteSubmissions(submissions);
        setSummary(dashboardSummary ?? null);
      })
      .catch(() => {
        // Keep the existing prototype data visible if authentication/API access is unavailable.
      });

    return () => { active = false; };
  }, []);

  const assignments = useMemo(() => {
    if (!remoteAssessments) return fallbackAssignments;

    return remoteAssessments.map((assessment) => {
      const submitted = remoteSubmissions.filter((item) => item.assessment === assessment.id).length;
      return {
        id: assessment.id,
        title: assessment.title,
        subject: assessment.assessment_type,
        className: assessment.lesson_session_title,
        due: formatDueDate(assessment.due_date),
        status: apiStatus(assessment.status),
        submitted,
        total: submitted
      };
    });
  }, [remoteAssessments, remoteSubmissions]);

  const stats = summary
    ? {
        observations: summary.evaluations,
        projects: summary.assessments,
        practical: summary.submissions,
        competency: summary.evaluations
          ? Math.round((summary.published_evaluations / summary.evaluations) * 100)
          : 0
      }
    : {
        observations: 128,
        projects: 24,
        practical: 56,
        competency: 82
      };

  return (
    <div>
      <PageHeader
        title="Assessments"
        description="We measure growth, not just marks — observations, practical work, and competencies over time." />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Observations Logged"
          value={stats.observations}
          icon="Eye"
          tone="brand"
          delta={12} />
        <StatCard
          label="Projects"
          value={stats.projects}
          icon="FolderKanban"
          tone="emerald" />
        <StatCard label="Practical Work" value={stats.practical} icon="Hand" tone="warm" />
        <StatCard
          label="Avg Competency"
          value={stats.competency}
          icon="Award"
          tone="emerald"
          delta={5} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card className="overflow-hidden">
            <CardHeader
              title="Assignments & Projects"
              subtitle="Submission & grading status" />

            <div className="overflow-x-auto mt-2">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800">
                    <th className="px-5 py-3">Work</th>
                    <th className="px-5 py-3 hidden sm:table-cell">Subject</th>
                    <th className="px-5 py-3">Progress</th>
                    <th className="px-5 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {assignments.map((a) => {
                    const progress = a.total > 0 ? 100 : 0;
                    return (
                      <tr
                        key={a.id}
                        className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                        <td className="px-5 py-3">
                          <p className="font-semibold text-slate-800 dark:text-slate-100">
                            {a.title}
                          </p>
                          <p className="text-xs text-slate-400">
                            {a.className} · Due {a.due}
                          </p>
                        </td>
                        <td className="px-5 py-3 hidden sm:table-cell text-slate-600 dark:text-slate-300">
                          {a.subject}
                        </td>
                        <td className="px-5 py-3">
                          <div className="flex items-center gap-2 w-28">
                            <div className="flex-1 h-1.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                              <div
                                className="h-full rounded-full bg-brand-500"
                                style={{ width: `${progress}%` }} />
                            </div>
                            <span className="text-xs font-semibold text-slate-500">
                              {remoteAssessments ? `${a.submitted} submissions` : `${a.submitted}/${a.total}`}
                            </span>
                          </div>
                        </td>
                        <td className="px-5 py-3">
                          <Badge tone={a.status === 'Grading' ? 'warm' : 'emerald'}>
                            {a.status}
                          </Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          <Card>
            <CardHeader
              title="Learning Outcomes Distribution"
              subtitle="Where the class sits across competencies" />
            <div className="px-5 pb-5 mt-3 space-y-3">
              {outcomes.map((o) =>
                <div key={o.label}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-semibold text-slate-700 dark:text-slate-200">
                      {o.label}
                    </span>
                    <span className="text-slate-400">{o.pct}%</span>
                  </div>
                  <div className="h-2.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${o.tone}`}
                      style={{ width: `${o.pct}%` }} />
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>

        <Card>
          <CardHeader title="Competency Profile" subtitle="Class average" />
          <div className="px-3 pb-4 pt-2">
            <CompetencyRadarChart />
          </div>
        </Card>
      </div>
    </div>
  );
}
