import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { PageHeader } from '../components/ui/PageHeader';
import { useApp } from '../context/AppContext';
import {
  completeLesson,
  listLessons,
  startLesson,
  syncLessonDay,
  type ApiLesson,
  type LessonStatus
} from '../lib/lessonsApi';

function localDateValue(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatTime(value: string) {
  if (!value) return '—';
  const [hours, minutes] = value.split(':');
  const date = new Date();
  date.setHours(Number(hours), Number(minutes), 0, 0);
  return new Intl.DateTimeFormat('en', { hour: 'numeric', minute: '2-digit' }).format(date);
}

function statusTone(status: LessonStatus): 'brand' | 'emerald' | 'warm' | 'slate' | 'rose' {
  if (status === 'IN_PROGRESS') return 'brand';
  if (status === 'COMPLETED') return 'emerald';
  if (status === 'CANCELLED' || status === 'MISSED') return 'rose';
  return 'warm';
}

function statusLabel(status: LessonStatus) {
  return status.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function Lessons() {
  const { role } = useApp();
  const [selectedDate, setSelectedDate] = useState(localDateValue());
  const [lessons, setLessons] = useState<ApiLesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadLessons = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (role === 'teacher') {
        await syncLessonDay(selectedDate);
      }
      const data = await listLessons({ lessonDate: selectedDate });
      setLessons(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load lessons.');
      setLessons([]);
    } finally {
      setLoading(false);
    }
  }, [role, selectedDate]);

  useEffect(() => {
    loadLessons();
  }, [loadLessons]);

  const sortedLessons = useMemo(
    () => [...lessons].sort((a, b) => a.start_time.localeCompare(b.start_time)),
    [lessons]
  );

  const completedCount = lessons.filter((lesson) => lesson.status === 'COMPLETED').length;
  const activeCount = lessons.filter((lesson) => lesson.status === 'IN_PROGRESS').length;

  async function handleStart(lesson: ApiLesson) {
    setActionId(lesson.id);
    setError(null);
    try {
      const updated = await startLesson(lesson.id);
      setLessons((current) => current.map((item) => item.id === updated.id ? updated : item));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to start lesson.');
    } finally {
      setActionId(null);
    }
  }

  async function handleComplete(lesson: ApiLesson) {
    setActionId(lesson.id);
    setError(null);
    try {
      const updated = await completeLesson(lesson.id);
      setLessons((current) => current.map((item) => item.id === updated.id ? updated : item));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to complete lesson.');
    } finally {
      setActionId(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="Lessons"
        description="Your timetable-driven teaching sessions, with live start and completion tracking."
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <input
              type="date"
              value={selectedDate}
              onChange={(event) => setSelectedDate(event.target.value)}
              className="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 outline-none focus:border-brand-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
            />
            <Button variant="secondary" onClick={loadLessons} disabled={loading}>Refresh</Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <Card className="p-5">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Scheduled for day</p>
          <p className="mt-2 text-3xl font-extrabold text-slate-900 dark:text-white">{lessons.length}</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">In progress</p>
          <p className="mt-2 text-3xl font-extrabold text-slate-900 dark:text-white">{activeCount}</p>
        </Card>
        <Card className="p-5">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Completed</p>
          <p className="mt-2 text-3xl font-extrabold text-slate-900 dark:text-white">{completedCount}</p>
        </Card>
      </div>

      {error && (
        <div className="mb-5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-900/50 dark:bg-rose-950/30 dark:text-rose-300">
          {error}
        </div>
      )}

      <Card className="overflow-hidden">
        {loading ? (
          <div className="px-5 py-12 text-center text-sm text-slate-400">Loading lessons…</div>
        ) : sortedLessons.length === 0 ? (
          <div className="px-5 py-12 text-center">
            <p className="font-semibold text-slate-700 dark:text-slate-200">No lessons scheduled for this date.</p>
            <p className="mt-1 text-sm text-slate-400">
              {role === 'teacher'
                ? 'Published timetable entries assigned to you will appear here automatically.'
                : 'No lesson sessions have been recorded for this date.'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {sortedLessons.map((lesson) => (
              <div key={lesson.id} className="p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="flex items-start gap-4 min-w-0">
                  <div className="shrink-0 rounded-2xl bg-slate-100 px-3 py-2 text-center dark:bg-slate-800">
                    <p className="text-sm font-extrabold text-slate-800 dark:text-slate-100">{formatTime(lesson.start_time)}</p>
                    <p className="text-xs text-slate-400">{formatTime(lesson.end_time)}</p>
                  </div>
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-display text-lg font-bold text-slate-900 dark:text-white">{lesson.subject_name}</h3>
                      <Badge tone={statusTone(lesson.status)}>{statusLabel(lesson.status)}</Badge>
                    </div>
                    <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                      {lesson.classroom_name} · {lesson.teacher_name}
                      {lesson.room ? ` · ${lesson.room}` : ''}
                    </p>
                    {(lesson.started_at || lesson.ended_at) && (
                      <p className="mt-1 text-xs text-slate-400">
                        {lesson.started_at ? `Started ${new Date(lesson.started_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : ''}
                        {lesson.started_at && lesson.ended_at ? ' · ' : ''}
                        {lesson.ended_at ? `Completed ${new Date(lesson.ended_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : ''}
                      </p>
                    )}
                  </div>
                </div>

                {role === 'teacher' && (
                  <div className="flex items-center gap-2 shrink-0">
                    {lesson.status === 'SCHEDULED' && (
                      <Button onClick={() => handleStart(lesson)} disabled={actionId === lesson.id}>Start Lesson</Button>
                    )}
                    {lesson.status === 'IN_PROGRESS' && (
                      <Button variant="emerald" onClick={() => handleComplete(lesson)} disabled={actionId === lesson.id}>Complete Lesson</Button>
                    )}
                    {lesson.status === 'COMPLETED' && (
                      <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">Lesson completed</span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
