import React from 'react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card, CardHeader } from '../components/ui/Card';
import { StatCard } from '../components/ui/StatCard';
import { Badge } from '../components/ui/Badge';
import { CompetencyRadarChart } from '../components/charts/Charts';
import { assignments } from '../lib/data';
const outcomes = [
{
  label: 'Emerging',
  pct: 18,
  tone: 'bg-warm-500'
},
{
  label: 'Developing',
  pct: 34,
  tone: 'bg-brand-500'
},
{
  label: 'Secure',
  pct: 32,
  tone: 'bg-emerald-500'
},
{
  label: 'Mastered',
  pct: 16,
  tone: 'bg-emerald-600'
}];

export function Assessments() {
  return (
    <div>
      <PageHeader
        title="Assessments"
        description="We measure growth, not just marks — observations, practical work, and competencies over time." />
      

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Observations Logged"
          value={128}
          icon="Eye"
          tone="brand"
          delta={12} />
        
        <StatCard
          label="Projects"
          value={24}
          icon="FolderKanban"
          tone="emerald" />
        
        <StatCard label="Practical Work" value={56} icon="Hand" tone="warm" />
        <StatCard
          label="Avg Competency"
          value="82"
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
                  {assignments.map((a) =>
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
                            style={{
                              width: `${a.submitted / a.total * 100}%`
                            }} />
                          
                          </div>
                          <span className="text-xs font-semibold text-slate-500">
                            {a.submitted}/{a.total}
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-3">
                        <Badge
                        tone={a.status === 'Grading' ? 'warm' : 'emerald'}>
                        
                          {a.status}
                        </Badge>
                      </td>
                    </tr>
                  )}
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
                    style={{
                      width: `${o.pct}%`
                    }} />
                  
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
    </div>);

}