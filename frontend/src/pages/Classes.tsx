import React, { useEffect, useMemo, useState } from 'react';
import { ArrowRightIcon, BookOpenIcon, PencilIcon, PlusIcon, UsersIcon, XIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { cn } from '../lib/utils';
import {
  ApiAcademicYear,
  ApiCambridgeStage,
  ApiClassroom,
  ApiSchool,
  ApiTeacher,
  ApiTerm,
  createClassroom,
  deactivateClassroom,
  listAcademicYears,
  listCambridgeStages,
  listClassrooms,
  listSchools,
  listTeachers,
  listTerms,
  updateClassroom,
} from '../lib/api';
import { useApp } from '../context/AppContext';

const accents = ['brand', 'emerald', 'warm'] as const;
const accent: Record<string, string> = {
  brand: 'bg-brand-600',
  emerald: 'bg-emerald-500',
  warm: 'bg-warm-500'
};

type FormState = {
  school: string;
  academic_year: string;
  term: string;
  cambridge_stage: string;
  name: string;
  code: string;
  capacity: string;
  primary_teacher: string;
};

const emptyForm: FormState = {
  school: '', academic_year: '', term: '', cambridge_stage: '', name: '', code: '', capacity: '30', primary_teacher: ''
};

export function Classes() {
  const { role } = useApp();
  const isAdmin = role === 'admin';
  const [classrooms, setClassrooms] = useState<ApiClassroom[]>([]);
  const [schools, setSchools] = useState<ApiSchool[]>([]);
  const [years, setYears] = useState<ApiAcademicYear[]>([]);
  const [terms, setTerms] = useState<ApiTerm[]>([]);
  const [stages, setStages] = useState<ApiCambridgeStage[]>([]);
  const [teachers, setTeachers] = useState<ApiTeacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [saving, setSaving] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<ApiClassroom | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);

  const loadClassrooms = async () => {
    const data = await listClassrooms({ active: true });
    setClassrooms(data);
  };

  useEffect(() => {
    let mounted = true;
    Promise.all([
      listClassrooms({ active: true }),
      listSchools(),
      listAcademicYears(),
      listCambridgeStages({ active: true }),
    ])
      .then(([classes, schoolData, yearData, stageData]) => {
        if (!mounted) return;
        setClassrooms(classes);
        setSchools(schoolData);
        setYears(yearData);
        setStages(stageData);
      })
      .catch((err) => mounted && setError(err instanceof Error ? err.message : 'Unable to load classes.'))
      .finally(() => mounted && setLoading(false));
    return () => { mounted = false; };
  }, []);

  const selectedYear = years.find((year) => year.id === form.academic_year);
  const availableYears = useMemo(
    () => isAdmin && form.school ? years.filter((year) => year.school === form.school) : years,
    [form.school, isAdmin, years]
  );

  useEffect(() => {
    if (!showForm || !form.academic_year) {
      setTerms([]);
      return;
    }
    listTerms({ academicYear: form.academic_year })
      .then(setTerms)
      .catch((err) => setFormError(err instanceof Error ? err.message : 'Unable to load terms.'));
  }, [form.academic_year, showForm]);

  useEffect(() => {
    if (!showForm || !form.school) {
      setTeachers([]);
      return;
    }
    listTeachers({ status: 'ACTIVE' })
      .then((data) => setTeachers(data.filter((teacher) => teacher.school === form.school)))
      .catch((err) => setFormError(err instanceof Error ? err.message : 'Unable to load teachers.'));
  }, [form.school, showForm]);

  const openCreate = () => {
    setEditing(null);
    setForm({ ...emptyForm, school: schools[0]?.id || '' });
    setFormError('');
    setShowForm(true);
  };

  const openEdit = (classroom: ApiClassroom) => {
    setEditing(classroom);
    setForm({
      school: classroom.school,
      academic_year: classroom.academic_year,
      term: classroom.term,
      cambridge_stage: classroom.cambridge_stage,
      name: classroom.name,
      code: classroom.code,
      capacity: String(classroom.capacity),
      primary_teacher: classroom.primary_teacher_id || '',
    });
    setFormError('');
    setShowForm(true);
  };

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setFormError('');
    try {
      const payload = {
        ...(isAdmin ? { school: form.school } : {}),
        academic_year: form.academic_year,
        term: form.term,
        cambridge_stage: form.cambridge_stage,
        name: form.name.trim(),
        code: form.code.trim().toUpperCase(),
        capacity: Number(form.capacity),
        primary_teacher: form.primary_teacher || null,
      };
      if (editing) await updateClassroom(editing.id, payload);
      else await createClassroom(payload);
      await loadClassrooms();
      setShowForm(false);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unable to save the class.');
    } finally {
      setSaving(false);
    }
  };

  const deactivate = async (classroom: ApiClassroom) => {
    if (!window.confirm(`Deactivate ${classroom.name}? Existing enrollment and assessment history will be preserved.`)) return;
    try {
      await deactivateClassroom(classroom.id);
      await loadClassrooms();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to deactivate the class.');
    }
  };

  return (
    <div>
      <PageHeader
        title="Classes"
        description="Our learning communities — each a prepared environment where children flourish together."
        action={isAdmin ? <Button onClick={openCreate}><PlusIcon className="h-4 w-4" /> Add Class</Button> : undefined}
      />

      {loading && <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">{[1, 2, 3].map((item) => <Card key={item} className="h-56 animate-pulse bg-slate-100 dark:bg-slate-800/60" />)}</div>}

      {!loading && error && <Card className="p-6"><p className="text-sm font-semibold text-red-600 dark:text-red-400">Unable to load classes</p><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{error}</p></Card>}

      {!loading && !error && classrooms.length === 0 && <Card className="p-8 text-center"><p className="font-display font-bold text-slate-800 dark:text-slate-100">No active classes yet</p><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{isAdmin ? 'Create the first classroom using Add Class.' : 'No active classes are available for your institution.'}</p></Card>}

      {!loading && !error && classrooms.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {classrooms.map((classroom, index) => {
            const color = accents[index % accents.length];
            return (
              <Card key={classroom.id} className="overflow-hidden hover:-translate-y-1 transition-transform">
                <div className={cn('h-2', accent[color])} />
                <div className="p-5">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="font-display text-lg font-extrabold text-slate-900 dark:text-white">{classroom.name}</h3>
                    <Badge tone="slate">{classroom.stage_name}</Badge>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">{classroom.academic_year_name} · Term {classroom.term_number}</p>
                  {classroom.primary_teacher_name && <p className="mt-2 text-xs font-semibold text-slate-600 dark:text-slate-300">Class Teacher · {classroom.primary_teacher_name}</p>}
                  <div className="grid grid-cols-3 gap-2 mt-5 text-center">
                    <Stat value={String(classroom.student_count)} label="Students" />
                    <Stat value={String(classroom.subject_count)} label="Subjects" />
                    <Stat value={`${classroom.capacity}`} label="Capacity" />
                  </div>
                  <div className="mt-5 flex items-center justify-between rounded-2xl bg-slate-50 dark:bg-slate-800/60 px-3.5 py-2.5">
                    <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400"><UsersIcon className="h-4 w-4" />{classroom.code}</div>
                    <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400"><BookOpenIcon className="h-4 w-4" />{classroom.subject_count} subjects</div>
                  </div>
                  <div className="mt-5 flex gap-2">
                    <Link to={`/classes/${classroom.id}`} className="flex-1 inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-100 dark:bg-slate-800 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-200/70 dark:hover:bg-slate-700 transition-colors">
                      Open class <ArrowRightIcon className="h-4 w-4" />
                    </Link>
                    {isAdmin && <button type="button" onClick={() => openEdit(classroom)} className="rounded-2xl border border-slate-200 dark:border-slate-700 px-3 text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800" title="Edit class"><PencilIcon className="h-4 w-4" /></button>}
                    {isAdmin && <button type="button" onClick={() => deactivate(classroom)} className="rounded-2xl border border-red-200 dark:border-red-900/60 px-3 text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30" title="Deactivate class"><XIcon className="h-4 w-4" /></button>}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {showForm && isAdmin && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4" role="dialog" aria-modal="true">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 px-6 py-5">
              <div><h2 className="font-display text-xl font-extrabold text-slate-900 dark:text-white">{editing ? 'Edit Class' : 'Add Class'}</h2><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Set the academic context and class teacher.</p></div>
              <button type="button" onClick={() => setShowForm(false)} className="rounded-xl p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"><XIcon className="h-5 w-5" /></button>
            </div>
            <form onSubmit={submit} className="p-6 space-y-5">
              {formError && <div className="rounded-2xl bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-300">{formError}</div>}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Field label="Institution"><select required disabled={!!editing} value={form.school} onChange={(e) => setForm({ ...form, school: e.target.value, academic_year: '', term: '', primary_teacher: '' })} className={inputClass}><option value="">Select institution</option>{schools.map((school) => <option key={school.id} value={school.id}>{school.name}</option>)}</select></Field>
                <Field label="Class Name"><input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className={inputClass} placeholder="Grade 4A" /></Field>
                <Field label="Class Code"><input required value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} className={inputClass} placeholder="G4A" /></Field>
                <Field label="Capacity"><input required min="1" max="255" type="number" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: e.target.value })} className={inputClass} /></Field>
                <Field label="Academic Year"><select required value={form.academic_year} onChange={(e) => setForm({ ...form, academic_year: e.target.value, term: '' })} className={inputClass}><option value="">Select academic year</option>{availableYears.map((year) => <option key={year.id} value={year.id}>{year.name}</option>)}</select></Field>
                <Field label="Term"><select required disabled={!form.academic_year} value={form.term} onChange={(e) => setForm({ ...form, term: e.target.value })} className={inputClass}><option value="">Select term</option>{terms.map((term) => <option key={term.id} value={term.id}>Term {term.term_number}</option>)}</select></Field>
                <Field label="Cambridge Stage"><select required value={form.cambridge_stage} onChange={(e) => setForm({ ...form, cambridge_stage: e.target.value })} className={inputClass}><option value="">Select stage</option>{stages.map((stage) => <option key={stage.id} value={stage.id}>{stage.name}</option>)}</select></Field>
                <Field label="Class Teacher"><select value={form.primary_teacher} disabled={!form.school} onChange={(e) => setForm({ ...form, primary_teacher: e.target.value })} className={inputClass}><option value="">No class teacher</option>{teachers.map((teacher) => <option key={teacher.id} value={teacher.id}>{teacher.full_name}{teacher.department_name ? ` · ${teacher.department_name}` : ''}</option>)}</select></Field>
              </div>
              {selectedYear && <p className="text-xs text-slate-400">{selectedYear.start_date} — {selectedYear.end_date}</p>}
              <div className="flex justify-end gap-3 pt-2"><Button type="button" variant="secondary" onClick={() => setShowForm(false)}>Cancel</Button><Button type="submit" disabled={saving}>{saving ? 'Saving…' : editing ? 'Save Changes' : 'Create Class'}</Button></div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}

const inputClass = 'w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-3.5 py-2.5 text-sm text-slate-800 dark:text-slate-100 outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 disabled:opacity-60';

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="block"><span className="mb-1.5 block text-xs font-semibold text-slate-600 dark:text-slate-300">{label}</span>{children}</label>;
}

function Stat({ value, label }: { value: string; label: string }) {
  return <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 py-2.5"><p className="font-display font-extrabold text-slate-800 dark:text-slate-100">{value}</p><p className="text-[11px] text-slate-400 font-medium">{label}</p></div>;
}
