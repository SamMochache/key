import React, { useEffect, useMemo, useState } from 'react';
import { CalendarClockIcon, CheckCircle2Icon, CopyIcon, Loader2Icon, PlusIcon, SaveIcon, Settings2Icon, Trash2Icon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { EmptyState } from '../components/ui/EmptyState';
import { listAcademicYears, listClassrooms, listSchools, listTerms, type ApiAcademicYear, type ApiClassroom, type ApiTerm, type School } from '../lib/api';
import { archiveTimetable, createPeriod, createTimetable, createTimetableEntry, createTimetableVersion, deleteTimetableEntry, listPeriods, listTeacherSubjects, listTimetableEntries, listTimetables, publishTimetable, type ApiPeriod, type ApiTeacherSubject, type ApiTimetable, type ApiTimetableEntry, type WeekDay } from '../lib/timetableApi';

const DAYS: Array<{ key: WeekDay; label: string }> = [
  { key: 'MONDAY', label: 'Monday' }, { key: 'TUESDAY', label: 'Tuesday' }, { key: 'WEDNESDAY', label: 'Wednesday' }, { key: 'THURSDAY', label: 'Thursday' }, { key: 'FRIDAY', label: 'Friday' },
];

export function Timetables() {
  const [years, setYears] = useState<ApiAcademicYear[]>([]);
  const [terms, setTerms] = useState<ApiTerm[]>([]);
  const [schools, setSchools] = useState<School[]>([]);
  const [classrooms, setClassrooms] = useState<ApiClassroom[]>([]);
  const [periods, setPeriods] = useState<ApiPeriod[]>([]);
  const [timetables, setTimetables] = useState<ApiTimetable[]>([]);
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedTerm, setSelectedTerm] = useState('');
  const [selectedSchool, setSelectedSchool] = useState('');
  const [selectedClassroom, setSelectedClassroom] = useState('');
  const [selectedTimetable, setSelectedTimetable] = useState('');
  const [entries, setEntries] = useState<ApiTimetableEntry[]>([]);
  const [assignments, setAssignments] = useState<ApiTeacherSubject[]>([]);
  const [entryOpen, setEntryOpen] = useState(false);
  const [periodOpen, setPeriodOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [entryForm, setEntryForm] = useState({ weekday: 'MONDAY' as WeekDay, period: '', classroom: '', teacher_subject: '', room: '' });
  const [periodForm, setPeriodForm] = useState({ name: '', sequence: '', start_time: '08:00', end_time: '08:45', is_break: false });

  const currentTimetable = useMemo(() => timetables.find((item) => item.id === selectedTimetable) || null, [timetables, selectedTimetable]);
  const gridEntries = useMemo(() => entries.filter((item) => !selectedClassroom || item.classroom === selectedClassroom), [entries, selectedClassroom]);

  useEffect(() => {
    Promise.all([listAcademicYears(), listSchools()]).then(([yearData, schoolData]) => {
      setYears(yearData); setSchools(schoolData);
      setSelectedYear(yearData.find((item) => item.is_current)?.id || yearData[0]?.id || '');
      setSelectedSchool(schoolData[0]?.id || '');
    }).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load timetable options.')).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedYear) return;
    listTerms({ academicYear: selectedYear }).then((data) => {
      setTerms(data); setSelectedTerm((current) => data.some((item) => item.id === current) ? current : (data.find((item) => item.is_current)?.id || data[0]?.id || ''));
    }).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load terms.'));
  }, [selectedYear]);

  useEffect(() => {
    if (!selectedYear || !selectedTerm) return;
    listClassrooms({ academicYear: selectedYear, term: selectedTerm, active: true }).then((data) => {
      setClassrooms(data); setSelectedClassroom((current) => data.some((item) => item.id === current) ? current : data[0]?.id || '');
    }).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load classes.'));
    listTimetables({ academicYear: selectedYear, term: selectedTerm }).then((data) => {
      setTimetables(data); setSelectedTimetable((current) => data.some((item) => item.id === current) ? current : data[0]?.id || '');
    }).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load timetables.'));
  }, [selectedYear, selectedTerm]);

  useEffect(() => {
    if (!selectedSchool) return;
    listPeriods(selectedSchool).then(setPeriods).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load periods.'));
  }, [selectedSchool]);

  useEffect(() => {
    if (!selectedTimetable) { setEntries([]); return; }
    Promise.all([
      listTimetableEntries({ timetable: selectedTimetable }),
      listTeacherSubjects({ classroom: selectedClassroom || undefined, academicYear: selectedYear, term: selectedTerm, active: true }),
    ]).then(([entryData, assignmentData]) => { setEntries(entryData); setAssignments(assignmentData); }).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load timetable entries.'));
  }, [selectedTimetable, selectedClassroom, selectedYear, selectedTerm]);

  const refreshTimetables = async (preferredId?: string) => {
    const data = await listTimetables({ academicYear: selectedYear, term: selectedTerm });
    setTimetables(data); setSelectedTimetable(preferredId && data.some((item) => item.id === preferredId) ? preferredId : data[0]?.id || '');
  };

  const newTimetable = async () => {
    if (!selectedYear || !selectedTerm || !selectedSchool) return;
    setSaving(true); setError('');
    try {
      const selected = terms.find((item) => item.id === selectedTerm);
      const created = await createTimetable({ school: selectedSchool, academic_year: selectedYear, term: selectedTerm, name: `Weekly Timetable ${new Date().getFullYear()}`, version: 1, status: 'DRAFT', effective_from: selected?.start_date });
      await refreshTimetables(created.id);
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to create timetable.'); } finally { setSaving(false); }
  };

  const addEntry = async () => {
    if (!selectedTimetable || !entryForm.period || !entryForm.classroom || !entryForm.teacher_subject) return;
    setSaving(true); setError('');
    try {
      await createTimetableEntry({ timetable: selectedTimetable, weekday: entryForm.weekday, period: entryForm.period, classroom: entryForm.classroom, teacher_subject: entryForm.teacher_subject, room: entryForm.room });
      setEntries(await listTimetableEntries({ timetable: selectedTimetable })); setEntryOpen(false); setEntryForm({ weekday: 'MONDAY', period: '', classroom: selectedClassroom, teacher_subject: '', room: '' });
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to add timetable entry.'); } finally { setSaving(false); }
  };

  const addPeriod = async () => {
    if (!selectedSchool || !periodForm.name || !periodForm.sequence) return;
    setSaving(true); setError('');
    try {
      const created = await createPeriod({ school: selectedSchool, ...periodForm, sequence: Number(periodForm.sequence) });
      setPeriods((current) => [...current, created].sort((a, b) => a.sequence - b.sequence)); setPeriodOpen(false); setPeriodForm({ name: '', sequence: '', start_time: '08:00', end_time: '08:45', is_break: false });
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to create period.'); } finally { setSaving(false); }
  };

  const publish = async () => {
    if (!currentTimetable) return;
    setSaving(true); setError('');
    try { const updated = await publishTimetable(currentTimetable.id); setTimetables((current) => current.map((item) => item.id === updated.id ? updated : item)); } catch (err) { setError(err instanceof Error ? err.message : 'Unable to publish timetable.'); } finally { setSaving(false); }
  };

  const archive = async () => {
    if (!currentTimetable) return;
    setSaving(true); setError('');
    try { const updated = await archiveTimetable(currentTimetable.id); setTimetables((current) => current.map((item) => item.id === updated.id ? updated : item)); } catch (err) { setError(err instanceof Error ? err.message : 'Unable to archive timetable.'); } finally { setSaving(false); }
  };

  const newVersion = async () => {
    if (!currentTimetable) return;
    setSaving(true); setError('');
    try { const created = await createTimetableVersion(currentTimetable.id); await refreshTimetables(created.id); } catch (err) { setError(err instanceof Error ? err.message : 'Unable to create a new timetable version.'); } finally { setSaving(false); }
  };

  const removeEntry = async (id: string) => {
    if (!currentTimetable || currentTimetable.status === 'PUBLISHED') return;
    setSaving(true); setError('');
    try { await deleteTimetableEntry(id); setEntries((current) => current.filter((item) => item.id !== id)); } catch (err) { setError(err instanceof Error ? err.message : 'Unable to delete entry.'); } finally { setSaving(false); }
  };

  return <div>
    <PageHeader title="Timetables" description="Build, version, publish, and manage the weekly teaching schedule for each academic period." actions={<div className="flex flex-wrap gap-2">
      <Button variant="secondary" onClick={() => setPeriodOpen(true)}><Settings2Icon className="h-4 w-4" /> Periods</Button>
      <Button onClick={newTimetable} disabled={saving || !selectedYear || !selectedTerm || !selectedSchool}><PlusIcon className="h-4 w-4" /> New timetable</Button>
    </div>} />

    {error && <Card className="mb-5 p-4"><p className="text-sm text-rose-600 dark:text-rose-400">{error}</p></Card>}

    <Card className="p-5 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Select label="Academic Year" value={selectedYear} onChange={setSelectedYear}>{years.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</Select>
        <Select label="Term" value={selectedTerm} onChange={setSelectedTerm}>{terms.map((item) => <option key={item.id} value={item.id}>Term {item.term_number}</option>)}</Select>
        <Select label="Classroom" value={selectedClassroom} onChange={setSelectedClassroom}><option value="">All classrooms</option>{classrooms.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</Select>
        <Select label="Timetable" value={selectedTimetable} onChange={setSelectedTimetable}><option value="">Select timetable</option>{timetables.map((item) => <option key={item.id} value={item.id}>{item.name} · v{item.version} · {item.status}</option>)}</Select>
      </div>
    </Card>

    {currentTimetable && <Card className="mb-6 overflow-hidden">
      <div className="px-6 py-5 border-b border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div><div className="flex items-center gap-2"><CalendarClockIcon className="h-5 w-5 text-brand-600" /><h2 className="font-display font-extrabold text-lg text-slate-800 dark:text-slate-100">{currentTimetable.name} · v{currentTimetable.version}</h2><Badge tone={currentTimetable.status === 'PUBLISHED' ? 'emerald' : currentTimetable.status === 'ARCHIVED' ? 'slate' : 'warm'}>{currentTimetable.status}</Badge></div><p className="text-sm text-slate-400 mt-1">Effective {currentTimetable.effective_from} {currentTimetable.effective_to ? `to ${currentTimetable.effective_to}` : 'onwards'} · {currentTimetable.entry_count} scheduled entries</p></div>
        <div className="flex flex-wrap gap-2">
          {currentTimetable.status !== 'PUBLISHED' && currentTimetable.status !== 'ARCHIVED' && <><Button variant="secondary" onClick={() => { setEntryForm((current) => ({ ...current, classroom: selectedClassroom })); setEntryOpen(true); }}><PlusIcon className="h-4 w-4" /> Add lesson</Button><Button onClick={publish} disabled={saving}><CheckCircle2Icon className="h-4 w-4" /> Publish</Button></>}
          {currentTimetable.status === 'PUBLISHED' && <Button variant="secondary" onClick={newVersion} disabled={saving}><CopyIcon className="h-4 w-4" /> New version</Button>}
          {currentTimetable.status !== 'ARCHIVED' && <Button variant="secondary" onClick={archive} disabled={saving}>Archive</Button>}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[920px] border-collapse">
          <thead><tr className="bg-slate-50 dark:bg-slate-900/70"><th className="w-40 px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-400 border-r border-slate-100 dark:border-slate-800">Period</th>{DAYS.map((day) => <th key={day.key} className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-400 border-r border-slate-100 dark:border-slate-800">{day.label}</th>)}</tr></thead>
          <tbody>{periods.map((period) => <tr key={period.id} className="border-t border-slate-100 dark:border-slate-800">
            <td className="px-4 py-3 align-top border-r border-slate-100 dark:border-slate-800"><p className="font-semibold text-sm text-slate-700 dark:text-slate-200">{period.name}{period.is_break ? ' · Break' : ''}</p><p className="text-xs text-slate-400">{period.start_time.slice(0, 5)}–{period.end_time.slice(0, 5)}</p></td>
            {DAYS.map((day) => <td key={day.key} className="p-2 align-top border-r border-slate-100 dark:border-slate-800 h-24">{gridEntries.filter((entry) => entry.period === period.id && entry.weekday === day.key).map((entry) => <div key={entry.id} className="group rounded-2xl bg-brand-50 dark:bg-brand-950/30 border border-brand-100 dark:border-brand-900/50 p-3 mb-1.5"><div className="flex justify-between gap-2"><p className="text-sm font-bold text-slate-800 dark:text-slate-100">{entry.subject_name}</p>{currentTimetable.status !== 'PUBLISHED' && <button onClick={() => removeEntry(entry.id)} className="opacity-0 group-hover:opacity-100 text-rose-500" title="Remove"><Trash2Icon className="h-3.5 w-3.5" /></button>}</div><p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{entry.classroom_name}</p><p className="text-xs text-slate-400 mt-0.5">{entry.teacher_name}{entry.room ? ` · ${entry.room}` : ''}</p></div>)}</td>)}
          </tr>)}</tbody>
        </table>
      </div>
      {periods.length === 0 && <div className="p-10"><EmptyState icon="CalendarClock" title="No periods configured" description="Add your school's teaching periods before building the weekly schedule." /></div>}
    </Card>}

    {!loading && !currentTimetable && <Card><EmptyState icon="CalendarClock" title="No timetable selected" description="Create a timetable for the selected academic year and term to start scheduling lessons." /></Card>}

    {entryOpen && <Modal title="Add timetable lesson" onClose={() => setEntryOpen(false)}>
      <div className="space-y-4">
        <Select label="Day" value={entryForm.weekday} onChange={(value) => setEntryForm({ ...entryForm, weekday: value as WeekDay })}>{DAYS.map((day) => <option key={day.key} value={day.key}>{day.label}</option>)}</Select>
        <Select label="Period" value={entryForm.period} onChange={(value) => setEntryForm({ ...entryForm, period: value })}><option value="">Select period</option>{periods.filter((item) => !item.is_break).map((item) => <option key={item.id} value={item.id}>{item.name} · {item.start_time.slice(0, 5)}–{item.end_time.slice(0, 5)}</option>)}</Select>
        <Select label="Classroom" value={entryForm.classroom} onChange={(value) => setEntryForm({ ...entryForm, classroom: value, teacher_subject: '' })}>{classrooms.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</Select>
        <Select label="Teacher / Subject" value={entryForm.teacher_subject} onChange={(value) => setEntryForm({ ...entryForm, teacher_subject: value })}><option value="">Select assignment</option>{assignments.filter((item) => item.classroom === entryForm.classroom).map((item) => <option key={item.id} value={item.id}>{item.subject_name} · {item.teacher_name}</option>)}</Select>
        <Input label="Room (optional)" value={entryForm.room} onChange={(value) => setEntryForm({ ...entryForm, room: value })} />
        <div className="flex justify-end gap-2 pt-2"><Button variant="secondary" onClick={() => setEntryOpen(false)}>Cancel</Button><Button onClick={addEntry} disabled={saving || !entryForm.period || !entryForm.classroom || !entryForm.teacher_subject}>{saving ? <Loader2Icon className="h-4 w-4 animate-spin" /> : <SaveIcon className="h-4 w-4" />} Save lesson</Button></div>
      </div>
    </Modal>}

    {periodOpen && <Modal title="School periods" onClose={() => setPeriodOpen(false)}>
      <div className="space-y-4"><div className="grid grid-cols-2 gap-3"><Input label="Name" value={periodForm.name} onChange={(value) => setPeriodForm({ ...periodForm, name: value })} /><Input label="Sequence" type="number" value={periodForm.sequence} onChange={(value) => setPeriodForm({ ...periodForm, sequence: value })} /></div><div className="grid grid-cols-2 gap-3"><Input label="Start" type="time" value={periodForm.start_time} onChange={(value) => setPeriodForm({ ...periodForm, start_time: value })} /><Input label="End" type="time" value={periodForm.end_time} onChange={(value) => setPeriodForm({ ...periodForm, end_time: value })} /></div><label className="flex items-center gap-2 text-sm font-semibold text-slate-600 dark:text-slate-300"><input type="checkbox" checked={periodForm.is_break} onChange={(event) => setPeriodForm({ ...periodForm, is_break: event.target.checked })} /> Break period</label><div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-3 space-y-2 max-h-48 overflow-auto">{periods.map((item) => <div key={item.id} className="flex items-center justify-between text-sm"><span className="font-semibold text-slate-700 dark:text-slate-200">{item.sequence}. {item.name}</span><span className="text-xs text-slate-400">{item.start_time.slice(0, 5)}–{item.end_time.slice(0, 5)}</span></div>)}</div><div className="flex justify-end gap-2"><Button variant="secondary" onClick={() => setPeriodOpen(false)}>Close</Button><Button onClick={addPeriod} disabled={saving || !periodForm.name || !periodForm.sequence}><PlusIcon className="h-4 w-4" /> Add period</Button></div></div>
    </Modal>}
  </div>;
}

function Select({ label, value, onChange, children }: { label: string; value: string; onChange: (value: string) => void; children: React.ReactNode }) { return <div><label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">{label}</label><select value={value} onChange={(event) => onChange(event.target.value)} className="w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100">{children}</select></div>; }
function Input({ label, value, onChange, type = 'text' }: { label: string; value: string; onChange: (value: string) => void; type?: string }) { return <div><label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">{label}</label><input type={type} value={value} onChange={(event) => onChange(event.target.value)} className="w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100" /></div>; }
function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) { return <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4"><div className="w-full max-w-lg rounded-3xl bg-white dark:bg-slate-900 shadow-2xl p-6"><div className="flex items-center justify-between mb-5"><h3 className="font-display font-extrabold text-lg text-slate-800 dark:text-slate-100">{title}</h3><button onClick={onClose} className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200">×</button></div>{children}</div></div>; }
