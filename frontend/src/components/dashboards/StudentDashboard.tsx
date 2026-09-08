import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { StarIcon, TargetIcon, BookOpenIcon, TrophyIcon, SparklesIcon, CheckCircle2Icon, AlertCircleIcon, CalendarDaysIcon } from 'lucide-react';
import { PageHeader } from '../ui/PageHeader';
import { Card, CardHeader } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useApp } from '../../context/AppContext';
import { listEnrollments, type ApiEnrollment } from '../../lib/api';
import { listAssessments, listSubmissions, listEvaluations, type ApiAssessment, type ApiSubmission, type ApiEvaluation } from '../../lib/assessmentsApi';

function formatDate(value: string | null) {
  if (!value) return 'No due date';
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(`${value}T00:00:00`));
}
function formatStatus(value: string) { return value.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, c => c.toUpperCase()); }

export function StudentDashboard({ name }: { name: string }) {
  const { user } = useApp();
  const [enrollments, setEnrollments] = useState<ApiEnrollment[]>([]);
  const [assessments, setAssessments] = useState<ApiAssessment[]>([]);
  const [submissions, setSubmissions] = useState<ApiSubmission[]>([]);
  const [evaluations, setEvaluations] = useState<ApiEvaluation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true); setError('');
      try {
        const [enrollmentData, assessmentData, submissionData] = await Promise.all([
          listEnrollments({ status: 'ACTIVE' }), listAssessments({ status: 'PUBLISHED' }), listSubmissions()
        ]);
        if (!mounted) return;
        setEnrollments(enrollmentData); setAssessments(assessmentData); setSubmissions(submissionData);
        const graded = submissionData.filter(s => s.status === 'GRADED');
        const evaluationLists = await Promise.all(graded.map(s => listEvaluations(s.id)));
        if (mounted) setEvaluations(evaluationLists.flat().filter(e => e.published));
      } catch (err) {
        if (mounted) setError(err instanceof Error ? err.message : 'Unable to load your learning data.');
      } finally { if (mounted) setLoading(false); }
    }
    void load();
    return () => { mounted = false; };
  }, [user?.id]);

  const activeEnrollment = enrollments[0];
  const submittedIds = useMemo(() => new Set(submissions.map(s => s.assessment)), [submissions]);
  const completedCount = assessments.filter(a => submittedIds.has(a.id)).length;
  const progress = assessments.length ? Math.round(completedCount / assessments.length * 100) : 0;
  const upcoming = useMemo(() => assessments.filter(a => !submittedIds.has(a.id)).sort((a,b) => (a.due_date || '9999-12-31').localeCompare(b.due_date || '9999-12-31')).slice(0,4), [assessments, submittedIds]);
  const recentSubmissions = useMemo(() => [...submissions].sort((a,b) => (b.updated_at || '').localeCompare(a.updated_at || '')).slice(0,4), [submissions]);
  const latestFeedback = evaluations.filter(e => e.narrative_feedback?.trim()).sort((a,b) => (b.published_at || '').localeCompare(a.published_at || ''))[0];
  const averageScore = useMemo(() => { const scores = evaluations.map(e => Number(e.percentage)).filter(Number.isFinite); return scores.length ? Math.round(scores.reduce((a,b) => a+b,0) / scores.length) : null; }, [evaluations]);

  return <div>
    <PageHeader title={`Hi ${name.split(' ')[0]}! 🌱`} description="Your learning dashboard, powered by your school records." />
    {error && <Card className="p-4 mb-6 border-rose-200 dark:border-rose-900/50"><div className="flex gap-3"><AlertCircleIcon className="h-5 w-5 text-rose-500 shrink-0" /><div><p className="text-sm font-semibold text-rose-700 dark:text-rose-300">Unable to load your learning data</p><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{error}</p></div></div></Card>}
    {loading ? <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">{[1,2,3,4].map(i => <Card key={i} className="h-40 animate-pulse bg-slate-100 dark:bg-slate-800/60" />)}</div> :
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <Card className="p-6 bg-brand-600 border-brand-600 text-white"><div className="flex items-start justify-between gap-4"><div><p className="text-brand-100 font-semibold">My learning progress</p><h2 className="font-display text-2xl font-extrabold mt-1">{activeEnrollment?.classroom_name || 'Class not assigned'}</h2><p className="text-brand-100 mt-2">{assessments.length ? `${completedCount} of ${assessments.length} published activities submitted.` : 'No published activities are available yet.'}</p></div><BookOpenIcon className="h-8 w-8 text-white/70" /></div><div className="mt-5 h-2 rounded-full bg-white/20 overflow-hidden"><div className="h-full rounded-full bg-white transition-all" style={{width:`${progress}%`}} /></div><div className="mt-2 flex justify-between text-xs text-brand-100"><span>{progress}% submitted</span>{activeEnrollment?.term_number ? <span>Term {activeEnrollment.term_number}</span> : null}</div></Card>
        <Card><CardHeader title="My Activities" subtitle="Published work from your teachers" /><div className="px-3 pb-3 mt-2 space-y-1">{upcoming.length ? upcoming.map(a => <Link key={a.id} to="/assessments" className="flex items-center gap-3 rounded-2xl px-3 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/60"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-500/15 dark:text-brand-300"><BookOpenIcon className="h-5 w-5" /></span><div className="flex-1 min-w-0"><p className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">{a.title}</p><p className="text-xs text-slate-400">{a.teacher_name} · {formatDate(a.due_date)}</p></div><Badge tone="warm">To do</Badge></Link>) : <EmptyMessage text={assessments.length ? 'You have completed all published activities.' : 'No published activities yet.'} />}</div></Card>
        <Card><CardHeader title="My Submissions" subtitle="Your latest submitted work" /><div className="px-3 pb-3 mt-2 space-y-1">{recentSubmissions.length ? recentSubmissions.map(s => { const a=assessments.find(x=>x.id===s.assessment); return <div key={s.id} className="flex items-center gap-3 rounded-2xl px-3 py-3"><CheckCircle2Icon className={`h-6 w-6 shrink-0 ${s.status==='GRADED'?'text-emerald-500':'text-brand-500'}`} /><div className="flex-1 min-w-0"><p className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">{a?.title || 'Assessment'}</p><p className="text-xs text-slate-400">{formatStatus(s.status)} · {s.submitted_at ? formatDate(s.submitted_at.slice(0,10)) : 'Not submitted'}</p></div><Badge tone={s.status==='GRADED'?'emerald':'brand'}>{formatStatus(s.status)}</Badge></div> }) : <EmptyMessage text="You have not submitted any work yet." />}</div></Card>
      </div>
      <div className="space-y-6">
        <Card className="p-5"><h3 className="font-display font-bold text-slate-800 dark:text-slate-100 mb-4">My Progress</h3><div className="grid grid-cols-2 gap-3"><ProgressStat icon={TargetIcon} label="Activities" value={`${completedCount}/${assessments.length}`} /><ProgressStat icon={TrophyIcon} label="Graded" value={String(evaluations.length)} /><ProgressStat icon={StarIcon} label="Average" value={averageScore===null?'—':`${averageScore}%`} /><ProgressStat icon={CalendarDaysIcon} label="Class" value={activeEnrollment?.classroom_name || '—'} /></div></Card>
        <Card><CardHeader title="My Learning Goals" action={<TargetIcon className="h-5 w-5 text-slate-300" />} /><div className="px-5 pb-5 mt-2 space-y-3">{upcoming.slice(0,3).map(a => <div key={a.id} className="flex items-start gap-3"><span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-500/15 text-brand-600 text-xs font-bold">•</span><div><p className="text-sm font-semibold text-slate-700 dark:text-slate-200">{a.title}</p><p className="text-xs text-slate-400 mt-0.5">{a.description || 'Complete the activity assigned by your teacher.'}</p></div></div>)}{!upcoming.length && <EmptyMessage text="No outstanding learning goals have been published." compact />}</div></Card>
        <Card className="p-5"><div className="flex items-center gap-2 mb-2"><SparklesIcon className="h-5 w-5 text-brand-600" /><h3 className="font-display font-bold text-slate-800 dark:text-slate-100">Teacher Feedback</h3></div>{latestFeedback ? <><p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">“{latestFeedback.narrative_feedback}”</p><p className="text-xs text-slate-400 mt-3">Published by your teacher</p></> : <p className="text-sm text-slate-500 dark:text-slate-400">No published teacher feedback yet.</p>}</Card>
        <Card className="p-5"><div className="flex items-center gap-2 mb-3"><TrophyIcon className="h-5 w-5 text-warm-500" /><h3 className="font-display font-bold text-slate-800 dark:text-slate-100">My Achievements</h3></div><div className="space-y-2">{completedCount>0 && <Achievement icon={CheckCircle2Icon} label="First activity submitted" />}{evaluations.length>0 && <Achievement icon={StarIcon} label="First activity graded" />}{evaluations.length>=3 && <Achievement icon={TrophyIcon} label="Three activities graded" />}{!completedCount&&!evaluations.length && <EmptyMessage text="Achievements will appear as you complete and receive feedback on your work." compact />}</div></Card>
      </div>
    </div>}
  </div>;
}
function EmptyMessage({text,compact=false}:{text:string;compact?:boolean}) { return <p className={compact?'text-xs text-slate-400':'px-3 py-6 text-center text-sm text-slate-400'}>{text}</p>; }
function ProgressStat({icon:Icon,label,value}:{icon:React.ElementType;label:string;value:string}) { return <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-3"><Icon className="h-4 w-4 text-brand-600" /><p className="text-lg font-extrabold text-slate-800 dark:text-slate-100 mt-2 truncate">{value}</p><p className="text-xs text-slate-400 mt-0.5">{label}</p></div>; }
function Achievement({icon:Icon,label}:{icon:React.ElementType;label:string}) { return <div className="flex items-center gap-3 rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-3"><span className="flex h-9 w-9 items-center justify-center rounded-xl bg-warm-50 text-warm-600 dark:bg-warm-500/15 dark:text-warm-300"><Icon className="h-4 w-4" /></span><span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{label}</span></div>; }
