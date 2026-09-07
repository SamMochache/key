import React from 'react';
import { AreaChart, Area, LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { attendanceTrend as fallbackAttendance, growthTrend as fallbackGrowth, competencyRadar as fallbackCompetency, classCompare as fallbackClasses } from '../../lib/data';

const tooltipStyle = { borderRadius: 16, border: '1px solid rgba(148,163,184,0.25)', boxShadow: '0 4px 24px rgba(16,24,40,0.08)', fontSize: 12, padding: '8px 12px', background: 'rgba(255,255,255,0.98)' };
type AttendancePoint = { month: string; rate: number };
type GrowthPoint = { term: string; practical: number; language: number; math: number; culture: number };
type ClassPoint = { name: string; growth: number; attendance: number };
type CompetencyPoint = { skill: string; value: number };

export function AttendanceAreaChart({ height = 220, data = fallbackAttendance as AttendancePoint[] }: { height?: number; data?: AttendancePoint[] }) {
  return <ResponsiveContainer width="100%" height={height}><AreaChart data={data} margin={{ top: 10, right: 8, left: -18, bottom: 0 }}><defs><linearGradient id="attGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#1D4ED8" stopOpacity={0.25} /><stop offset="100%" stopColor="#1D4ED8" stopOpacity={0} /></linearGradient></defs><CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.18)" vertical={false} /><XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} /><YAxis domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} /><Tooltip contentStyle={tooltipStyle} /><Area type="monotone" dataKey="rate" stroke="#1D4ED8" strokeWidth={2.5} fill="url(#attGrad)" name="Attendance %" /></AreaChart></ResponsiveContainer>;
}
export function GrowthLineChart({ height = 260, data = fallbackGrowth as GrowthPoint[] }: { height?: number; data?: GrowthPoint[] }) {
  return <ResponsiveContainer width="100%" height={height}><LineChart data={data} margin={{ top: 10, right: 8, left: -18, bottom: 0 }}><CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.18)" vertical={false} /><XAxis dataKey="term" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} /><YAxis domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} /><Tooltip contentStyle={tooltipStyle} /><Line type="monotone" dataKey="practical" stroke="#10B981" strokeWidth={2.5} dot={false} name="Practical Life" /><Line type="monotone" dataKey="language" stroke="#1D4ED8" strokeWidth={2.5} dot={false} name="Language" /><Line type="monotone" dataKey="math" stroke="#F59E0B" strokeWidth={2.5} dot={false} name="Mathematics" /><Line type="monotone" dataKey="culture" stroke="#8b5cf6" strokeWidth={2.5} dot={false} name="Culture" /></LineChart></ResponsiveContainer>;
}
export function CompetencyRadarChart({ height = 260, data = fallbackCompetency as CompetencyPoint[] }: { height?: number; data?: CompetencyPoint[] }) {
  return <ResponsiveContainer width="100%" height={height}><RadarChart data={data} outerRadius="72%"><PolarGrid stroke="rgba(148,163,184,0.25)" /><PolarAngleAxis dataKey="skill" tick={{ fontSize: 11, fill: '#94a3b8' }} /><PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} /><Radar dataKey="value" stroke="#10B981" fill="#10B981" fillOpacity={0.25} strokeWidth={2} /><Tooltip contentStyle={tooltipStyle} /></RadarChart></ResponsiveContainer>;
}
export function ClassCompareBar({ height = 260, data = fallbackClasses as ClassPoint[] }: { height?: number; data?: ClassPoint[] }) {
  return <ResponsiveContainer width="100%" height={height}><BarChart data={data} margin={{ top: 10, right: 8, left: -18, bottom: 0 }} barGap={6}><CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.18)" vertical={false} /><XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} /><YAxis domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} /><Tooltip contentStyle={tooltipStyle} cursor={{ fill: 'rgba(148,163,184,0.08)' }} /><Bar dataKey="growth" fill="#1D4ED8" radius={[8, 8, 0, 0]} name="Growth" /><Bar dataKey="attendance" fill="#10B981" radius={[8, 8, 0, 0]} name="Attendance" /></BarChart></ResponsiveContainer>;
}
