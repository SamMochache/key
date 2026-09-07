import React, { useEffect, useMemo, useState } from 'react';
import { CheckIcon, XIcon, ClockIcon, ShieldCheckIcon, SaveIcon, RefreshCwIcon, LockIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Avatar } from '../components/ui/Avatar';
import { StatCard } from '../components/ui/StatCard';
import { Badge } from '../components/ui/Badge';
import { listLessons, syncLessonDay, type ApiLesson } from '../lib/lessonsApi';
import { listAttendance, listClassEnrollments, lockAttendance, saveAttendance, type AttendanceStatus, type ApiAttendanceRegister } from '../lib/attendanceApi';
import { cn } from '../lib/utils';

type Mark = AttendanceStatus;
const options: { key: Mark; label: string; icon: React.ReactNode; active: string }[] = [
  { key: 'PRESENT', label: 'Present', icon: <CheckIcon className="h-4 w-4" />, active: 'bg-emerald-500 text-white' },
  { key: 'LATE', label: 'Late', icon: <ClockIcon className="h-4 w-4" />, active: 'bg-warm-500 text-white' },
  { key: 'ABSENT', label: 'Absent', icon: <XIcon className="h-4 w-4" />, active: 'bg-rose-500 text-white' },
  { key: 'EXCUSED', label: 'Excused', icon: <ShieldCheckIcon className="h-4 w-4" />, active: 'bg-brand-600 text-white' },
];
function today() { const date = new Date(); return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 10); }

export function Attendance() {
  const [date, setDate] = useState(today);
  const [lessons, setLessons] = useState<ApiLesson[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [register, setRegister] = useState<ApiAttendanceRegister | null>(null);
  const [enrollments, setEnrollments] = useState<Awaited<ReturnType<typeof listClassEnrollments>>>([]);
  const [marks, setMarks] = useState<Record<string, Mark>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const selectedLesson = lessons.find((lesson) => lesson.id === selectedId) ?? null;
  const editable = !!selectedLesson && (selectedLesson.status === 'IN_PROGRESS' || selectedLesson.status === 'COMPLETED') && register?.status !== 'LOCKED';
  const counts = useMemo(() => Object.values(marks).reduce((acc, status) => ({ ...acc, [status]: acc[status] + 1 }), { PRESENT: 0, ABSENT: 0, LATE: 0, EXCUSED: 0 } as Record<Mark, number>), [marks]);

  async function loadLessons(targetDate = date) {
    setLoading(true); setError(''); setNotice('');
    try {
      await syncLessonDay(targetDate);
      const data = await listLessons({ lessonDate: targetDate });
      setLessons(data); setSelectedId((current) => data.some((item) => item.id === current) ? current : data[0]?.id ?? '');
    } catch (err) { setLessons([]); setSelectedId(''); setError(err instanceof Error ? err.message : 'Unable to load lessons.'); }
    finally { setLoading(false); }
  }
  useEffect(() => { void loadLessons(); }, [date]);

  useEffect(() => {
    if (!selectedLesson) { setRegister(null); setEnrollments([]); setMarks({}); return; }
    let cancelled = false;
    (async () => {
      setError(''); setNotice('');
      try {
        const [registers, roster] = await Promise.all([listAttendance({ lessonSession: selectedLesson.id }), listClassEnrollments(selectedLesson.classroom)]);
        if (cancelled) return;
        const existing = registers[0] ?? null; setRegister(existing); setEnrollments(roster);
        const next: Record<string, Mark> = {}; roster.forEach((enrollment) => { next[enrollment.id] = 'PRESENT'; });
        existing?.records.forEach((record) => { next[record.enrollment] = record.status; }); setMarks(next);
      } catch (err) { if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load attendance roster.'); }
    })();
    return () => { cancelled = true; };
  }, [selectedId, selectedLesson?.classroom]);

  async function handleSave(submit = false) {
    if (!selectedLesson || !editable) return; setSaving(true); setError(''); setNotice('');
    try {
      const saved = await saveAttendance({ lesson_session: selectedLesson.id, submit, records: enrollments.map((enrollment) => ({ enrollment: enrollment.id, status: marks[enrollment.id] ?? 'PRESENT' })) });
      setRegister(saved); setNotice(submit ? 'Attendance submitted successfully.' : 'Attendance saved successfully.');
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to save attendance.'); }
    finally { setSaving(false); }
  }
  async function handleLock() {
    if (!register) return; setSaving(true); setError('');
    try { setRegister(await lockAttendance(register.id)); setNotice('Attendance register locked.'); }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to lock attendance.'); }
    finally { setSaving(false); }
  }
  const titleDate = new Date(`${date}T00:00:00`).toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

  return <div>
    <PageHeader title="Attendance" description="Record attendance against the actual lesson session — saved to the institution record." actions={<div className="flex flex-wrap gap-2"><input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900" /><Button variant="secondary" onClick={() => void loadLessons()} disabled={loading}><RefreshCwIcon className={cn('h-4 w-4', loading && 'animate-spin')} /> Refresh</Button></div>} />
    {error && <div className="mb-5 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}
    {notice && <div className="mb-5 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{notice}</div>}
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6"><StatCard label="Present" value={counts.PRESENT} icon="Check" tone="emerald" /><StatCard label="Late" value={counts.LATE} icon="Clock" tone="warm" /><StatCard label="Absent" value={counts.ABSENT} icon="X" tone="rose" /><StatCard label="Excused" value={counts.EXCUSED} icon="ShieldCheck" tone="brand" /></div>
    <Card className="mb-6"><CardHeader title="Lesson sessions" subtitle={titleDate} /><div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 px-5 pb-5">
      {lessons.map((lesson) => <button key={lesson.id} onClick={() => setSelectedId(lesson.id)} className={cn('text-left rounded-xl border p-4 transition', selectedId === lesson.id ? 'border-brand-500 bg-brand-50/60 dark:bg-brand-950/20' : 'border-slate-200 hover:border-slate-300 dark:border-slate-700')}><div className="flex items-start justify-between gap-3"><div><p className="font-semibold text-sm text-slate-800 dark:text-slate-100">{lesson.subject_name}</p><p className="text-xs text-slate-500 mt-1">{lesson.classroom_name} · {lesson.start_time.slice(0, 5)}–{lesson.end_time.slice(0, 5)}</p></div><Badge tone={lesson.status === 'COMPLETED' ? 'emerald' : lesson.status === 'IN_PROGRESS' ? 'brand' : 'slate'}>{lesson.status.replace('_', ' ')}</Badge></div></button>)}
      {!loading && lessons.length === 0 && <p className="text-sm text-slate-500 py-4">No timetable lessons were found for this date.</p>}
    </div></Card>
    {selectedLesson && <Card className="overflow-hidden"><CardHeader title={`${selectedLesson.subject_name} · ${selectedLesson.classroom_name}`} subtitle={`${titleDate} · ${selectedLesson.start_time.slice(0, 5)}–${selectedLesson.end_time.slice(0, 5)}`} actions={<div className="flex gap-2">{register?.status === 'SUBMITTED' && <Button variant="secondary" onClick={() => void handleLock()} disabled={saving}><LockIcon className="h-4 w-4" /> Lock</Button>}<Button variant="secondary" onClick={() => void handleSave(false)} disabled={!editable || saving}><SaveIcon className="h-4 w-4" /> {saving ? 'Saving…' : 'Save'}</Button><Button variant="emerald" onClick={() => void handleSave(true)} disabled={!editable || saving}>Submit attendance</Button></div>} />
      {!editable && <div className="mx-5 mt-3 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-500 dark:bg-slate-800/60">Start the lesson from Lessons before recording attendance. Submitted and locked registers cannot be edited.</div>}
      <div className="mt-3 divide-y divide-slate-100 dark:divide-slate-800">{enrollments.map((enrollment) => <div key={enrollment.id} className="flex flex-col sm:flex-row sm:items-center gap-3 px-5 py-3"><div className="flex items-center gap-3 flex-1"><Avatar name={enrollment.student_name} size={40} /><div><p className="font-semibold text-sm text-slate-800 dark:text-slate-100">{enrollment.student_name}</p><p className="text-xs text-slate-400">{enrollment.admission_number}</p></div></div><div className="flex gap-1.5">{options.map((option) => <button key={option.key} disabled={!editable} onClick={() => setMarks((current) => ({ ...current, [enrollment.id]: option.key }))} className={cn('inline-flex items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-xs font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50', marks[enrollment.id] === option.key ? option.active : 'bg-slate-100 text-slate-500 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700')} title={option.label}>{option.icon}<span className="hidden sm:inline">{option.label}</span></button>)}</div></div>)}{!enrollments.length && <p className="px-5 py-8 text-sm text-slate-500">No active students are enrolled in this class for the lesson term.</p>}</div>
    </Card>}
  </div>;
}
