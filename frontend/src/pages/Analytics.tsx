import React from 'react';
import { PageHeader } from '../components/ui/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { Card, CardHeader } from '../components/ui/Card';
import {
  AttendanceAreaChart,
  GrowthLineChart,
  ClassCompareBar,
  CompetencyRadarChart } from
'../components/charts/Charts';
export function Analytics() {
  return (
    <div>
      <PageHeader
        title="Analytics"
        description="Interactive insight into attendance, growth, and learning outcomes across the school." />
      

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Growth Index"
          value={84}
          icon="TrendingUp"
          tone="emerald"
          delta={6} />
        
        <StatCard
          label="Attendance"
          value="94%"
          icon="CalendarCheck"
          tone="brand"
          delta={2} />
        
        <StatCard
          label="Assignment Completion"
          value="88%"
          icon="ClipboardCheck"
          tone="warm"
          delta={3} />
        
        <StatCard
          label="Outcomes Secure+"
          value="48%"
          icon="Award"
          tone="emerald"
          delta={4} />
        
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Attendance Trends" subtitle="School-wide" />
          <div className="px-3 pb-4 pt-2">
            <AttendanceAreaChart height={240} />
          </div>
        </Card>
        <Card>
          <CardHeader
            title="Student Growth"
            subtitle="Learning areas over the year" />
          
          <div className="px-3 pb-4 pt-2">
            <GrowthLineChart height={240} />
          </div>
        </Card>
        <Card>
          <CardHeader
            title="Class Comparisons"
            subtitle="Growth vs attendance" />
          
          <div className="px-3 pb-4 pt-2">
            <ClassCompareBar height={240} />
          </div>
        </Card>
        <Card>
          <CardHeader title="Learning Outcomes" subtitle="Competency profile" />
          <div className="px-3 pb-4 pt-2">
            <CompetencyRadarChart height={240} />
          </div>
        </Card>
      </div>
    </div>);

}