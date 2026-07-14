import React from 'react';
import * as Icons from 'lucide-react';
import { DownloadIcon, ArrowRightIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { cn } from '../lib/utils';
const reports = [
{
  title: 'Attendance Report',
  desc: 'Presence rates by class, month, and student.',
  icon: 'CalendarCheck',
  tone: 'brand',
  to: '/analytics'
},
{
  title: 'Class Report',
  desc: 'A snapshot of each learning community.',
  icon: 'School',
  tone: 'emerald',
  to: '/classes'
},
{
  title: 'Student Progress Report',
  desc: 'Growth across all learning areas.',
  icon: 'TrendingUp',
  tone: 'warm',
  to: '/students'
},
{
  title: 'AI Narrative Report',
  desc: 'Warm, growth-focused stories per child.',
  icon: 'Sparkles',
  tone: 'emerald',
  to: '/ai-reports'
},
{
  title: 'Performance Analytics',
  desc: 'Outcomes, trends, and comparisons.',
  icon: 'BarChart3',
  tone: 'brand',
  to: '/analytics'
},
{
  title: 'Teacher Report',
  desc: 'Workload, observations, and grading.',
  icon: 'GraduationCap',
  tone: 'warm',
  to: '/classes'
}];

const tone: Record<string, string> = {
  brand: 'bg-brand-50 text-brand-600 dark:bg-brand-600/20 dark:text-brand-300',
  emerald:
  'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-300',
  warm: 'bg-warm-50 text-warm-600 dark:bg-warm-500/20 dark:text-warm-300'
};
export function Reports() {
  return (
    <div>
      <PageHeader
        title="Reports"
        description="Generate beautiful, printable reports for families, staff, and leadership." />
      

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map((r) => {
          const Icon = (Icons as any)[r.icon] ?? Icons.FileText;
          return (
            <Card
              key={r.title}
              className="p-5 flex flex-col hover:-translate-y-0.5 transition-transform">
              
              <span
                className={cn(
                  'flex h-12 w-12 items-center justify-center rounded-2xl mb-4',
                  tone[r.tone]
                )}>
                
                <Icon className="h-5 w-5" />
              </span>
              <h3 className="font-display font-bold text-slate-800 dark:text-slate-100">
                {r.title}
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 flex-1">
                {r.desc}
              </p>
              <div className="flex items-center gap-2 mt-4">
                <Link
                  to={r.to}
                  className="inline-flex items-center gap-1.5 text-sm font-bold text-brand-600 hover:gap-2 transition-all">
                  
                  Open <ArrowRightIcon className="h-4 w-4" />
                </Link>
                <button className="ml-auto inline-flex items-center gap-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-200/70 dark:hover:bg-slate-700">
                  <DownloadIcon className="h-3.5 w-3.5" /> PDF
                </button>
              </div>
            </Card>);

        })}
      </div>
    </div>);

}