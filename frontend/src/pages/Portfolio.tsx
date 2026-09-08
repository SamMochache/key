import React, { useEffect, useMemo, useState } from 'react';
import { AwardIcon, ExternalLinkIcon, FileTextIcon, ImageIcon, PlusIcon, UploadIcon, VideoIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { getCurrentUser, listEnrollments, listStudents, listSubmissions, type ApiStudent, type ApiSubmission } from '../lib/api';
import {
  createPortfolio, createPortfolioArtifact, createPortfolioItem, getMyPortfolio, listPortfolioItems, listPortfolios,
  updatePortfolio, type ApiPortfolio, type ApiPortfolioItem, type PortfolioItemType,
} from '../lib/portfolioApi';

const itemTypes: Array<[PortfolioItemType, string]> = [
  ['PROJECT', 'Project'], ['ARTWORK', 'Artwork'], ['PHOTO', 'Photo'], ['VIDEO', 'Video'],
  ['AUDIO', 'Audio'], ['CERTIFICATE', 'Certificate'], ['OBSERVATION', 'Observation'],
  ['PRESENTATION', 'Presentation'], ['ASSESSMENT', 'Assessment'], ['OTHER', 'Other'],
];
const icons: Record<string, React.ElementType> = {
  PROJECT: FileTextIcon, ARTWORK: ImageIcon, PHOTO: ImageIcon, VIDEO: VideoIcon,
  AUDIO: VideoIcon, CERTIFICATE: AwardIcon, OBSERVATION: FileTextIcon, PRESENTATION: FileTextIcon,
  ASSESSMENT: FileTextIcon, OTHER: FileTextIcon,
};

export function Portfolio() {
  const [role, setRole] = useState('');
  const [portfolios, setPortfolios] = useState<ApiPortfolio[]>([]);
  const [students, setStudents] = useState<ApiStudent[]>([]);
  const [portfolio, setPortfolio] = useState<ApiPortfolio | null>(null);
  const [items, setItems] = useState<ApiPortfolioItem[]>([]);
  const [submissions, setSubmissions] = useState<ApiSubmission[]>([]);
  const [studentEnrollmentIds, setStudentEnrollmentIds] = useState<Set<string>>(new Set());
  const [selectedPortfolio, setSelectedPortfolio] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [showPortfolioForm, setShowPortfolioForm] = useState(false);
  const [summary, setSummary] = useState('');
  const [portfolioStudent, setPortfolioStudent] = useState('');
  const [form, setForm] = useState({ title: '', description: '', item_type: 'PROJECT' as PortfolioItemType, event_date: new Date().toISOString().slice(0, 10), assessment_submission: '', file: null as File | null, caption: '' });
  const isStudent = role === 'student';
  const canWrite = ['admin', 'teacher', 'student'].includes(role);

  async function load(currentRole = role) {
    setLoading(true); setError('');
    try {
      const user = await getCurrentUser();
      const resolvedRole = currentRole || user.role;
      setRole(resolvedRole);
      const [current, allPortfolios, submissionData, studentData, ownEnrollments] = await Promise.all([
        resolvedRole === 'student' ? getMyPortfolio() : Promise.resolve(null),
        resolvedRole === 'student' ? Promise.resolve([]) : listPortfolios(),
        ['admin', 'teacher', 'student'].includes(resolvedRole) ? listSubmissions() : Promise.resolve([]),
        ['admin', 'teacher'].includes(resolvedRole) ? listStudents({ isActive: true }) : Promise.resolve([]),
        resolvedRole === 'student' ? listEnrollments({ status: 'ACTIVE' }) : Promise.resolve([]),
      ]);
      setPortfolio(current);
      setPortfolios(allPortfolios);
      setSubmissions(submissionData);
      setStudents(studentData);
      setStudentEnrollmentIds(new Set(ownEnrollments.map((enrollment) => enrollment.id)));
      const activeId = current?.id || selectedPortfolio || allPortfolios[0]?.id || '';
      setSelectedPortfolio(activeId);
      if (activeId) {
        const target = current || allPortfolios.find((p) => p.id === activeId) || null;
        setPortfolio(target);
        setSummary(target?.summary || '');
        setItems(await listPortfolioItems({ portfolio: activeId }));
      } else setItems([]);
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to load portfolio.'); }
    finally { setLoading(false); }
  }

  useEffect(() => { void load(); }, []);

  const selectedStudentName = portfolio?.student_name || portfolios.find((p) => p.id === selectedPortfolio)?.student_name || 'Learner';
  const visibleSubmissions = useMemo(() => {
    if (isStudent) return submissions.filter((submission) => studentEnrollmentIds.has(submission.enrollment));
    return submissions.filter((submission) => !portfolio || submission.student_name === portfolio.student_name);
  }, [isStudent, submissions, portfolio, studentEnrollmentIds]);

  async function saveSummary() {
    if (!portfolio) return;
    setSaving(true); setError('');
    try { const updated = await updatePortfolio(portfolio.id, summary); setPortfolio(updated); setPortfolios((all) => all.map((p) => p.id === updated.id ? updated : p)); }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to save portfolio summary.'); }
    finally { setSaving(false); }
  }

  async function handleCreatePortfolio(event: React.FormEvent) {
    event.preventDefault();
    if (!portfolioStudent) return;
    setSaving(true); setError('');
    try {
      const created = await createPortfolio(portfolioStudent);
      setPortfolios((all) => [...all, created]);
      setSelectedPortfolio(created.id);
      setPortfolio(created);
      setSummary('');
      setPortfolioStudent('');
      setShowPortfolioForm(false);
      setItems([]);
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to create portfolio.'); }
    finally { setSaving(false); }
  }

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    if (!portfolio || !form.title.trim()) return;
    setSaving(true); setError('');
    try {
      const item = await createPortfolioItem({ portfolio: portfolio.id, item_type: form.item_type, title: form.title.trim(), description: form.description.trim(), event_date: form.event_date, assessment_submission: form.assessment_submission || null });
      if (form.file) await createPortfolioArtifact(item.id, form.file, form.caption.trim());
      setForm({ title: '', description: '', item_type: 'PROJECT', event_date: new Date().toISOString().slice(0, 10), assessment_submission: '', file: null, caption: '' });
      setShowForm(false); await load(role);
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to save portfolio item.'); }
    finally { setSaving(false); }
  }

  return <div>
    <PageHeader title="Learning Portfolio" description="A living collection of each learner’s creations, milestones, and moments of growth." actions={canWrite && portfolio ? <Button onClick={() => setShowForm((v) => !v)}><PlusIcon className="h-4 w-4" /> Add to portfolio</Button> : canWrite && !isStudent ? <Button onClick={() => setShowPortfolioForm((v) => !v)}><PlusIcon className="h-4 w-4" /> Create portfolio</Button> : undefined} />
    {error && <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}

    {!isStudent && portfolios.length > 0 && <Card className="mb-6 p-4"><label className="block text-sm font-medium text-slate-700 dark:text-slate-200">Learner portfolio</label><select value={selectedPortfolio} onChange={async (e) => { const id = e.target.value; setSelectedPortfolio(id); const p = portfolios.find((x) => x.id === id) || null; setPortfolio(p); setSummary(p?.summary || ''); setItems(id ? await listPortfolioItems({ portfolio: id }) : []); }} className="mt-1.5 w-full max-w-2xl rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">Select portfolio</option>{portfolios.map((p) => <option key={p.id} value={p.id}>{p.student_name} — {p.admission_number}</option>)}</select></Card>}

    {!isStudent && showPortfolioForm && <Card className="mb-6 p-5"><form onSubmit={handleCreatePortfolio} className="space-y-4"><label className="block text-sm font-medium text-slate-700 dark:text-slate-200">Learner<select required value={portfolioStudent} onChange={(e) => setPortfolioStudent(e.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">Select learner</option>{students.filter((s) => !portfolios.some((p) => p.student === s.id)).map((s) => <option key={s.id} value={s.id}>{s.full_name} — {s.admission_number}</option>)}</select></label><div className="flex justify-end gap-2"><Button type="button" variant="secondary" onClick={() => setShowPortfolioForm(false)}>Cancel</Button><Button type="submit" disabled={saving}>{saving ? 'Creating…' : 'Create portfolio'}</Button></div></form></Card>}

    {loading ? <Card className="p-8 text-center text-sm text-slate-500">Loading portfolio…</Card> : !portfolio ? <Card className="p-8 text-center"><p className="font-semibold text-slate-800 dark:text-slate-100">No portfolio selected</p><p className="mt-1 text-sm text-slate-500">Select an existing learner portfolio or create one for a learner.</p></Card> : <>
      <Card className="mb-6 p-5"><div className="flex flex-col gap-4 md:flex-row md:items-end"><div className="flex-1"><p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{selectedStudentName}</p><h2 className="mt-1 text-xl font-bold text-slate-800 dark:text-slate-100">Learning story</h2><textarea value={summary} onChange={(e) => setSummary(e.target.value)} rows={3} placeholder="Add a short learner profile or reflection…" className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900" /></div><Button onClick={saveSummary} disabled={saving}>{saving ? 'Saving…' : 'Save summary'}</Button></div></Card>

      {canWrite && showForm && <Card className="mb-6 p-5"><form onSubmit={handleCreate} className="space-y-4"><div className="grid grid-cols-1 gap-4 md:grid-cols-2"><label className="text-sm font-medium text-slate-700 dark:text-slate-200">Type<select value={form.item_type} onChange={(e) => setForm({ ...form, item_type: e.target.value as PortfolioItemType })} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900">{itemTypes.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></label><label className="text-sm font-medium text-slate-700 dark:text-slate-200">Date<input type="date" value={form.event_date} onChange={(e) => setForm({ ...form, event_date: e.target.value })} required className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900" /></label></div><label className="block text-sm font-medium text-slate-700 dark:text-slate-200">Title<input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900" placeholder="e.g. Robotics prototype" /></label><label className="block text-sm font-medium text-slate-700 dark:text-slate-200">Description<textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900" /></label>{visibleSubmissions.length > 0 && <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">Assessment submission (optional)<select value={form.assessment_submission} onChange={(e) => setForm({ ...form, assessment_submission: e.target.value })} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">None</option>{visibleSubmissions.map((s) => <option key={s.id} value={s.id}>{s.student_name} — {s.admission_number}</option>)}</select></label>}<div className="grid grid-cols-1 gap-4 md:grid-cols-2"><label className="text-sm font-medium text-slate-700 dark:text-slate-200">Artifact file<input type="file" onChange={(e) => setForm({ ...form, file: e.target.files?.[0] || null })} className="mt-1.5 block w-full text-sm text-slate-500" /></label><label className="text-sm font-medium text-slate-700 dark:text-slate-200">Caption<input value={form.caption} onChange={(e) => setForm({ ...form, caption: e.target.value })} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900" /></label></div><div className="flex justify-end gap-2"><Button type="button" variant="secondary" onClick={() => setShowForm(false)}>Cancel</Button><Button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save item'}</Button></div></form></Card>}

      {items.length === 0 ? <Card className="p-8 text-center"><p className="font-semibold text-slate-800 dark:text-slate-100">No portfolio items yet</p><p className="mt-1 text-sm text-slate-500">Add projects, artwork, certificates, observations, or assessment evidence as the learner progresses.</p></Card> : <div className="columns-1 gap-6 sm:columns-2 lg:columns-3 [column-fill:_balance]">{items.map((item) => { const Icon = icons[item.item_type] || FileTextIcon; const artifact = item.artifacts[0]; return <Card key={item.id} className="mb-6 overflow-hidden break-inside-avoid"><div className="p-5"><div className="flex items-start justify-between gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100 text-slate-500 dark:bg-slate-800"><Icon className="h-4 w-4" /></span><Badge tone={item.item_type === 'ARTWORK' || item.item_type === 'PHOTO' ? 'warm' : item.item_type === 'CERTIFICATE' ? 'brand' : 'emerald'}>{item.item_type_label}</Badge></div><h3 className="mt-4 font-semibold text-slate-800 dark:text-slate-100">{item.title}</h3><p className="mt-1 text-xs text-slate-400">{new Date(item.event_date).toLocaleDateString()} · {item.student_name}</p>{item.assessment_title && <p className="mt-2 text-xs font-medium text-slate-500">Assessment: {item.assessment_title}</p>}{item.description && <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{item.description}</p>}{artifact?.file_url && <a href={artifact.file_url} target="_blank" rel="noreferrer" className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:underline"><UploadIcon className="h-3.5 w-3.5" /> Open artifact <ExternalLinkIcon className="h-3.5 w-3.5" /></a>}</div></Card>; })}</div>}
    </>}
  </div>;
}
