import React, { useEffect, useMemo, useState } from 'react';
import { CalendarDaysIcon, ChevronLeftIcon, ChevronRightIcon, MapPinIcon, PlusIcon, Trash2Icon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { EmptyState } from '../components/ui/EmptyState';
import { listAcademicYears, listTerms, type ApiAcademicYear, type ApiTerm } from '../lib/api';
import { createCalendarEvent, deleteCalendarEvent, listCalendarEvents, type ApiCalendarEvent, type CalendarEventType } from '../lib/calendarApi';
import { cn } from '../lib/utils';

const TYPES: Array<{ value: CalendarEventType; label: string }> = [
  { value: 'ACADEMIC', label: 'Academic' }, { value: 'HOLIDAY', label: 'Holiday' }, { value: 'EXAMINATION', label: 'Examination' },
  { value: 'MEETING', label: 'Meeting' }, { value: 'ACTIVITY', label: 'Activity' }, { value: 'DEADLINE', label: 'Deadline' }, { value: 'OTHER', label: 'Other' },
];
const tone: Record<CalendarEventType, string> = { ACADEMIC: 'bg-brand-500', HOLIDAY: 'bg-emerald-500', EXAMINATION: 'bg-rose-500', MEETING: 'bg-warm-500', ACTIVITY: 'bg-indigo-500', DEADLINE: 'bg-orange-500', OTHER: 'bg-slate-500' };

function toInputDateTime(value: Date) { const pad = (n: number) => String(n).padStart(2, '0'); return `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())}T${pad(value.getHours())}:${pad(value.getMinutes())}`; }

export function Calendar() {
  const [years, setYears] = useState<ApiAcademicYear[]>([]);
  const [terms, setTerms] = useState<ApiTerm[]>([]);
  const [year, setYear] = useState('');
  const [term, setTerm] = useState('');
  const [month, setMonth] = useState(() => new Date());
  const [events, setEvents] = useState<ApiCalendarEvent[]>([]);
  const [typeFilter, setTypeFilter] = useState('');
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ title: '', event_type: 'ACADEMIC' as CalendarEventType, start_at: '', end_at: '', all_day: true, location: '', description: '' });

  const monthStart = useMemo(() => new Date(month.getFullYear(), month.getMonth(), 1), [month]);
  const monthEnd = useMemo(() => new Date(month.getFullYear(), month.getMonth() + 1, 0, 23, 59, 59), [month]);
  const days = useMemo(() => Array.from({ length: monthEnd.getDate() }, (_, i) => new Date(month.getFullYear(), month.getMonth(), i + 1)), [month, monthEnd]);
  const leading = monthStart.getDay();

  useEffect(() => {
    Promise.all([listAcademicYears(), listTerms()]).then(([y, t]) => {
      setYears(y); setTerms(t);
      const selectedYear = y.find((item) => item.is_current)?.id || y[0]?.id || '';
      setYear(selectedYear);
      const selectedTerm = t.find((item) => item.is_current && item.academic_year === selectedYear)?.id || t.find((item) => item.academic_year === selectedYear)?.id || '';
      setTerm(selectedTerm);
    }).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load calendar options.')).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!year) return;
    const first = new Date(month.getFullYear(), month.getMonth(), 1);
    const last = new Date(month.getFullYear(), month.getMonth() + 1, 0, 23, 59, 59);
    listCalendarEvents({ academicYear: year, term: term || undefined, start: first.toISOString(), end: last.toISOString(), eventType: typeFilter || undefined })
      .then(setEvents).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load calendar events.'));
  }, [year, term, month, typeFilter]);

  useEffect(() => {
    if (!year) return;
    listTerms({ academicYear: year }).then((data) => { setTerms(data); setTerm((current) => data.some((item) => item.id === current) ? current : data.find((item) => item.is_current)?.id || data[0]?.id || ''); }).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load terms.'));
  }, [year]);

  const eventsByDay = useMemo(() => events.reduce<Record<number, ApiCalendarEvent[]>>((acc, event) => { const d = new Date(event.start_at).getDate(); (acc[d] ||= []).push(event); return acc; }, {}), [events]);
  const monthLabel = month.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });

  const addEvent = async () => {
    if (!year || !form.title || !form.start_at || !form.end_at) return;
    setSaving(true); setError('');
    try {
      const created = await createCalendarEvent({ academic_year: year, term: term || null, ...form, start_at: new Date(form.start_at).toISOString(), end_at: new Date(form.end_at).toISOString() });
      setEvents((current) => [...current, created].sort((a, b) => a.start_at.localeCompare(b.start_at))); setOpen(false);
      setForm({ title: '', event_type: 'ACADEMIC', start_at: '', end_at: '', all_day: true, location: '', description: '' });
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to create event.'); } finally { setSaving(false); }
  };

  const removeEvent = async (id: string) => {
    if (!window.confirm('Delete this calendar event?')) return;
    setSaving(true); setError('');
    try { await deleteCalendarEvent(id); setEvents((current) => current.filter((event) => event.id !== id)); } catch (err) { setError(err instanceof Error ? err.message : 'Unable to delete event.'); } finally { setSaving(false); }
  };

  return <div>
    <PageHeader title="Academic Calendar" description="Exams, activities, meetings, deadlines and holidays — the rhythm of the school year." actions={<Button onClick={() => { const start = new Date(month.getFullYear(), month.getMonth(), Math.min(new Date().getDate(), monthEnd.getDate()), 8); const end = new Date(start.getTime() + 60 * 60 * 1000); setForm((current) => ({ ...current, start_at: toInputDateTime(start), end_at: toInputDateTime(end) })); setOpen(true); }}><PlusIcon className="h-4 w-4" /> Add event</Button>} />
    {error && <Card className="mb-5 p-4"><p className="text-sm text-rose-600 dark:text-rose-400">{error}</p></Card>}
    <Card className="p-5 mb-6"><div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Select label="Academic Year" value={year} onChange={setYear}>{years.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</Select>
      <Select label="Term" value={term} onChange={setTerm}><option value="">All terms</option>{terms.filter((item) => item.academic_year === year).map((item) => <option key={item.id} value={item.id}>Term {item.term_number}</option>)}</Select>
      <Select label="Event type" value={typeFilter} onChange={setTypeFilter}><option value="">All types</option>{TYPES.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</Select>
    </div></Card>
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2"><Card className="p-5">
        <div className="flex items-center justify-between mb-5"><div><h2 className="font-display text-xl font-extrabold text-slate-900 dark:text-white">{monthLabel}</h2><p className="text-sm text-slate-400 mt-1">{events.length} event{events.length === 1 ? '' : 's'} this month</p></div><div className="flex gap-2"><Button variant="secondary" onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() - 1, 1))}><ChevronLeftIcon className="h-4 w-4" /></Button><Button variant="secondary" onClick={() => setMonth(new Date())}>Today</Button><Button variant="secondary" onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() + 1, 1))}><ChevronRightIcon className="h-4 w-4" /></Button></div></div>
        <div className="grid grid-cols-7 gap-2 text-center text-xs font-bold text-slate-400 mb-2">{['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((d) => <span key={d}>{d}</span>)}</div>
        <div className="grid grid-cols-7 gap-2">{Array.from({ length: leading }).map((_, i) => <span key={`empty-${i}`} />)}{days.map((day) => { const dayEvents = eventsByDay[day.getDate()] || []; const today = new Date(); const isToday = day.toDateString() === today.toDateString(); return <div key={day.toISOString()} className={cn('min-h-[92px] rounded-2xl border p-1.5 text-left', isToday ? 'border-brand-500 bg-brand-50 dark:bg-brand-600/15' : 'border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/60')}><span className={cn('text-xs font-bold', isToday ? 'text-brand-600' : 'text-slate-500 dark:text-slate-400')}>{day.getDate()}</span><div className="mt-1 space-y-1">{dayEvents.slice(0, 3).map((event) => <div key={event.id} className={cn('group rounded-md px-1.5 py-0.5 text-[10px] font-semibold text-white truncate', tone[event.event_type])} title={event.title}>{event.title}<button onClick={() => removeEvent(event.id)} className="hidden group-hover:inline float-right ml-1" title="Delete"><Trash2Icon className="h-3 w-3" /></button></div>)}{dayEvents.length > 3 && <p className="text-[10px] text-slate-400">+{dayEvents.length - 3} more</p>}</div></div>; })}</div>
      </Card></div>
      <Card className="p-5"><div className="flex items-center gap-2 mb-4"><CalendarDaysIcon className="h-5 w-5 text-brand-600" /><h2 className="font-display font-extrabold text-lg text-slate-800 dark:text-slate-100">Upcoming</h2></div>{loading ? <p className="text-sm text-slate-400">Loading…</p> : events.length === 0 ? <EmptyState icon="CalendarDays" title="No events" description="There are no calendar events matching the selected period." /> : <div className="space-y-3">{events.slice(0, 8).map((event) => <div key={event.id} className="rounded-2xl border border-slate-100 dark:border-slate-800 p-3"><div className="flex items-start justify-between gap-3"><div><Badge tone="slate">{TYPES.find((item) => item.value === event.event_type)?.label || event.event_type}</Badge><p className="font-bold text-sm text-slate-800 dark:text-slate-100 mt-2">{event.title}</p><p className="text-xs text-slate-400 mt-1">{new Date(event.start_at).toLocaleString([], { dateStyle: 'medium', timeStyle: event.all_day ? undefined : 'short' })}</p>{event.location && <p className="text-xs text-slate-400 mt-1 flex items-center gap-1"><MapPinIcon className="h-3 w-3" />{event.location}</p>}</div><button onClick={() => removeEvent(event.id)} className="text-slate-300 hover:text-rose-500"><Trash2Icon className="h-4 w-4" /></button></div></div>)}</div>}</Card>
    </div>
    {open && <div className="fixed inset-0 z-50 bg-slate-950/40 flex items-center justify-center p-4"><Card className="w-full max-w-lg p-6"><div className="flex items-center justify-between mb-5"><h2 className="font-display text-xl font-extrabold">Add calendar event</h2><button onClick={() => setOpen(false)} className="text-slate-400">×</button></div><div className="space-y-4"><Field label="Title" value={form.title} onChange={(value) => setForm({ ...form, title: value })} /><Select label="Type" value={form.event_type} onChange={(value) => setForm({ ...form, event_type: value as CalendarEventType })}>{TYPES.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</Select><div className="grid grid-cols-2 gap-3"><Field label="Starts" type="datetime-local" value={form.start_at} onChange={(value) => setForm({ ...form, start_at: value })} /><Field label="Ends" type="datetime-local" value={form.end_at} onChange={(value) => setForm({ ...form, end_at: value })} /></div><label className="flex items-center gap-2 text-sm text-slate-600"><input type="checkbox" checked={form.all_day} onChange={(e) => setForm({ ...form, all_day: e.target.checked })} /> All day</label><Field label="Location" value={form.location} onChange={(value) => setForm({ ...form, location: value })} /><label className="block text-sm font-semibold text-slate-600">Description<textarea className="mt-1 w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-transparent p-3 text-sm" rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label><div className="flex justify-end gap-2 pt-2"><Button variant="secondary" onClick={() => setOpen(false)}>Cancel</Button><Button onClick={addEvent} disabled={saving || !form.title || !form.start_at || !form.end_at}>Save event</Button></div></div></Card></div>}
  </div>;
}

function Select({ label, value, onChange, children }: { label: string; value: string; onChange: (value: string) => void; children: React.ReactNode }) { return <label className="block text-sm font-semibold text-slate-600 dark:text-slate-300">{label}<select className="mt-1 w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3 text-sm" value={value} onChange={(e) => onChange(e.target.value)}>{children}</select></label>; }
function Field({ label, value, onChange, type = 'text' }: { label: string; value: string; onChange: (value: string) => void; type?: string }) { return <label className="block text-sm font-semibold text-slate-600 dark:text-slate-300">{label}<input type={type} className="mt-1 w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3 text-sm" value={value} onChange={(e) => onChange(e.target.value)} /></label>; }
