import React, { useEffect, useState } from 'react';
import { PageHeader } from '../components/ui/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { Card, CardHeader } from '../components/ui/Card';
import { AttendanceAreaChart, GrowthLineChart, ClassCompareBar, CompetencyRadarChart } from '../components/charts/Charts';
import { getAnalytics, AnalyticsData } from '../lib/api';

const metric = (value: number | null, suffix = '') => value === null ? '—' : `${value}${suffix}`;

export function Analytics() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    getAnalytics().then((result) => { if (active) setData(result); }).catch((err) => { if (active) setError(err instanceof Error ? err.message : 'Unable to load analytics.'); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const summary = data?.summary;
  const noData = Boolean(data && summary?.students === 0 && data.class_compare.length === 0 && data.competency_radar.length === 0);

  return <div>
    <PageHeader title="Analytics" description="Interactive insight into attendance, growth, and learning outcomes across the school." />
    {error && <Card><div className="p-5 text-sm text-red-600">Unable to load live analytics: {error}</div></Card>}
    {loading ? <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">{[1,2,3,4].map((item) => <div key={item} className="h-28 rounded-2xl bg-slate-100 animate-pulse" />)}</div> : <>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Growth Index" value={metric(summary?.growth_index ?? null)} icon="TrendingUp" tone="emerald" />
        <StatCard label="Attendance" value={metric(summary?.attendance_rate ?? null, '%')} icon="CalendarCheck" tone="brand" />
        <StatCard label="Assignment Completion" value={metric(summary?.assignment_completion ?? null, '%')} icon="ClipboardCheck" tone="warm" />
        <StatCard label="Outcomes Secure+" value={metric(summary?.outcomes_secure ?? null, '%')} icon="Award" tone="emerald" />
      </div>
      {noData ? <Card><div className="p-8 text-center"><h3 className="text-sm font-semibold text-slate-900">Not enough data yet</h3><p className="mt-1 text-sm text-slate-500">Analytics will populate as attendance, assessments, evaluations, and competency evidence are recorded.</p></div></Card> : <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card><CardHeader title="Attendance Trends" subtitle="School-wide" /><div className="px-3 pb-4 pt-2"><AttendanceAreaChart height={240} data={data?.attendance_trend} /></div></Card>
        <Card><CardHeader title="Student Growth" subtitle="Learning areas over the year" /><div className="px-3 pb-4 pt-2"><GrowthLineChart height={240} data={data?.growth_trend} /></div></Card>
        <Card><CardHeader title="Class Comparisons" subtitle="Growth vs attendance" /><div className="px-3 pb-4 pt-2"><ClassCompareBar height={240} data={data?.class_compare} /></div></Card>
        <Card><CardHeader title="Learning Outcomes" subtitle="Competency profile" /><div className="px-3 pb-4 pt-2"><CompetencyRadarChart height={240} data={data?.competency_radar} /></div></Card>
      </div>}
    </>}
  </div>;
}
