import React, { useEffect, useMemo, useState } from 'react';
import { ExternalLinkIcon, FileTextIcon, ImageIcon, LinkIcon, PlusIcon, VideoIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { getCurrentUser } from '../lib/api';
import { listSubmissions, type ApiSubmission } from '../lib/assessmentsApi';
import { createEvidence, listEvidence, type ApiEvidence, type EvidenceType } from '../lib/evidenceApi';

const typeLabels: Record<EvidenceType, string> = {
  DOCUMENT: 'Document',
  IMAGE: 'Image',
  VIDEO: 'Video',
  LINK: 'Link',
  OBSERVATION: 'Observation',
  OTHER: 'Other',
};

const typeIcons: Record<EvidenceType, React.ElementType> = {
  DOCUMENT: FileTextIcon,
  IMAGE: ImageIcon,
  VIDEO: VideoIcon,
  LINK: LinkIcon,
  OBSERVATION: FileTextIcon,
  OTHER: FileTextIcon,
};

export function Evidence() {
  const [role, setRole] = useState('');
  const [submissions, setSubmissions] = useState<ApiSubmission[]>([]);
  const [evidence, setEvidence] = useState<ApiEvidence[]>([]);
  const [selectedSubmission, setSelectedSubmission] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', evidence_type: 'DOCUMENT' as EvidenceType, url: '', file: null as File | null });

  const canCreate = role === 'admin' || role === 'teacher';

  async function load() {
    setLoading(true);
    setError('');
    try {
      const [user, submissionData, evidenceData] = await Promise.all([
        getCurrentUser(),
        listSubmissions(),
        listEvidence(),
      ]);
      setRole(user.role);
      setSubmissions(submissionData);
      setEvidence(evidenceData);
      if (!selectedSubmission && submissionData.length) setSelectedSubmission(submissionData[0].id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load evidence.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, []);

  const visibleEvidence = useMemo(() => {
    if (!selectedSubmission) return evidence;
    return evidence.filter((item) => item.submission === selectedSubmission);
  }, [evidence, selectedSubmission]);

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    if (!selectedSubmission || !form.title.trim()) return;
    setSaving(true);
    setError('');
    try {
      await createEvidence({
        submission: selectedSubmission,
        title: form.title.trim(),
        description: form.description.trim(),
        evidence_type: form.evidence_type,
        url: form.url.trim(),
        file: form.file,
      });
      setForm({ title: '', description: '', evidence_type: 'DOCUMENT', url: '', file: null });
      setShowForm(false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save evidence.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Evidence"
        description="Capture authentic learner work and connect it to the assessment record."
        actions={canCreate ? <Button onClick={() => setShowForm((value) => !value)}><PlusIcon className="h-4 w-4" /> Add evidence</Button> : undefined}
      />

      {error && <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}

      {canCreate && showForm && (
        <Card className="mb-6 p-5">
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-200">
                Submission
                <select value={selectedSubmission} onChange={(e) => setSelectedSubmission(e.target.value)} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900">
                  <option value="">Select submission</option>
                  {submissions.map((item) => <option key={item.id} value={item.id}>{item.student_name} — {item.admission_number}</option>)}
                </select>
              </label>
              <label className="text-sm font-medium text-slate-700 dark:text-slate-200">
                Evidence type
                <select value={form.evidence_type} onChange={(e) => setForm({ ...form, evidence_type: e.target.value as EvidenceType })} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900">
                  {Object.entries(typeLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
              </label>
            </div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">Title<input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900" placeholder="e.g. Robotics prototype demonstration" /></label>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">Description<textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900" placeholder="What does this evidence demonstrate?" /></label>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-200">URL<input type="url" value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900" placeholder="https://..." /></label>
              <label className="text-sm font-medium text-slate-700 dark:text-slate-200">File<input type="file" onChange={(e) => setForm({ ...form, file: e.target.files?.[0] || null })} className="mt-1.5 block w-full text-sm text-slate-500" /></label>
            </div>
            <div className="flex justify-end gap-2"><Button type="button" variant="secondary" onClick={() => setShowForm(false)}>Cancel</Button><Button type="submit" disabled={saving || !selectedSubmission}>{saving ? 'Saving…' : 'Save evidence'}</Button></div>
          </form>
        </Card>
      )}

      <Card className="mb-6 p-4">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">Submission</label>
        <select value={selectedSubmission} onChange={(e) => setSelectedSubmission(e.target.value)} className="mt-1.5 w-full max-w-2xl rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-900">
          <option value="">All submissions</option>
          {submissions.map((item) => <option key={item.id} value={item.id}>{item.student_name} — {item.admission_number} — {item.assessment}</option>)}
        </select>
      </Card>

      {loading ? <Card className="p-8 text-center text-sm text-slate-500">Loading evidence…</Card> : visibleEvidence.length === 0 ? (
        <Card className="p-8 text-center"><p className="font-semibold text-slate-800 dark:text-slate-100">No evidence yet</p><p className="mt-1 text-sm text-slate-500">Evidence added to assessment submissions will appear here.</p></Card>
      ) : (
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          {visibleEvidence.map((item) => {
            const Icon = typeIcons[item.evidence_type] || FileTextIcon;
            return <Card key={item.id} className="p-5">
              <div className="flex items-start justify-between gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100 text-slate-500 dark:bg-slate-800"><Icon className="h-4 w-4" /></span><Badge tone="brand">{typeLabels[item.evidence_type]}</Badge></div>
              <h3 className="mt-4 font-semibold text-slate-800 dark:text-slate-100">{item.title}</h3>
              <p className="mt-1 text-xs text-slate-400">{item.student_name} · {item.assessment_title}</p>
              {item.description && <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{item.description}</p>}
              {(item.file_url || item.url) && <a href={item.file_url || item.url} target="_blank" rel="noreferrer" className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:underline">Open evidence <ExternalLinkIcon className="h-3.5 w-3.5" /></a>}
            </Card>;
          })}
        </div>
      )}
    </div>
  );
}
