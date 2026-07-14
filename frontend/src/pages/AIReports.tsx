import React, { useState, useRef } from 'react';
import * as Icons from 'lucide-react';
import {
  SparklesIcon,
  PrinterIcon,
  CheckCircle2Icon,
  Loader2Icon,
  PencilIcon,
  SendIcon } from
'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { EmptyState } from '../components/ui/EmptyState';
import { students, LOGO_URL } from '../lib/data';
import {
  buildReport,
  competencyScores,
  type ReportSection } from
'../lib/aiReport';
type Phase = 'idle' | 'thinking' | 'streaming' | 'ready' | 'published';
const TERMS = ['Term 1', 'Term 2', 'Term 3', 'Term 4'];
const SUBJECTS = [
'Language',
'Mathematics',
'Practical Life',
'Culture & Science',
'Overall'];

function SectionIcon({ name }: {name: string;}) {
  const Cmp = (Icons as any)[name] ?? Icons.FileText;
  return <Cmp className="h-4 w-4" />;
}
export function AIReports() {
  const [studentId, setStudentId] = useState(students[0].id);
  const [term, setTerm] = useState('Term 2');
  const [subject, setSubject] = useState('Overall');
  const [phase, setPhase] = useState<Phase>('idle');
  const [sections, setSections] = useState<ReportSection[]>([]);
  const [visibleCount, setVisibleCount] = useState(0);
  const [editing, setEditing] = useState(false);
  const timers = useRef<number[]>([]);
  const student = students.find((s) => s.id === studentId)!;
  const clearTimers = () => {
    timers.current.forEach((t) => window.clearTimeout(t));
    timers.current = [];
  };
  const generate = () => {
    clearTimers();
    setEditing(false);
    setPhase('thinking');
    setVisibleCount(0);
    const full = buildReport(student.name, subject, term);
    setSections(full);
    timers.current.push(
      window.setTimeout(() => {
        setPhase('streaming');
        full.forEach((_, i) => {
          timers.current.push(
            window.setTimeout(
              () => {
                setVisibleCount(i + 1);
                if (i === full.length - 1) setPhase('ready');
              },
              350 * (i + 1)
            )
          );
        });
      }, 1400)
    );
  };
  const updateSection = (key: string, content: string) => {
    setSections((prev) =>
    prev.map((s) =>
    s.key === key ?
    {
      ...s,
      content
    } :
    s
    )
    );
  };
  return (
    <div>
      <PageHeader
        title="AI Student Reports"
        description="Generate warm, growth-focused narrative reports. Review, refine, and publish to parents — beauty over marks."
        actions={
        phase === 'ready' || phase === 'published' ?
        <>
              <Button variant="secondary" onClick={() => setEditing((e) => !e)}>
                <PencilIcon className="h-4 w-4" />{' '}
                {editing ? 'Done editing' : 'Edit'}
              </Button>
              <Button variant="secondary" onClick={() => window.print()}>
                <PrinterIcon className="h-4 w-4" /> Export PDF
              </Button>
              <Button
            variant="emerald"
            onClick={() => setPhase('published')}
            disabled={phase === 'published'}>
            
                {phase === 'published' ?
            <CheckCircle2Icon className="h-4 w-4" /> :

            <SendIcon className="h-4 w-4" />
            }
                {phase === 'published' ? 'Published' : 'Publish'}
              </Button>
            </> :
        undefined
        } />
      

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="no-print">
          <Card className="p-5 sticky top-24">
            <h3 className="font-display font-bold text-slate-800 dark:text-slate-100 mb-4">
              Report Parameters
            </h3>
            <div className="space-y-4">
              <Field label="Student">
                <div className="flex items-center gap-3 rounded-2xl border border-slate-200 dark:border-slate-700 p-2">
                  <Avatar src={student.avatar} name={student.name} size={36} />
                  <select
                    value={studentId}
                    onChange={(e) => setStudentId(e.target.value)}
                    className="flex-1 bg-transparent text-sm font-semibold text-slate-800 dark:text-slate-100 outline-none">
                    
                    {students.
                    filter((s) => s.status === 'Enrolled').
                    map((s) =>
                    <option key={s.id} value={s.id}>
                          {s.name} — {s.className}
                        </option>
                    )}
                  </select>
                </div>
              </Field>
              <Field label="Term">
                <Select value={term} onChange={setTerm} options={TERMS} />
              </Field>
              <Field label="Class / Subject">
                <Select
                  value={subject}
                  onChange={setSubject}
                  options={SUBJECTS} />
                
              </Field>

              <Button
                className="w-full"
                onClick={generate}
                disabled={phase === 'thinking' || phase === 'streaming'}>
                
                {phase === 'thinking' || phase === 'streaming' ?
                <Loader2Icon className="h-4 w-4 animate-spin" /> :

                <SparklesIcon className="h-4 w-4" />
                }
                {phase === 'idle' ? 'Generate AI Report' : 'Regenerate'}
              </Button>
              <p className="text-xs text-slate-400 text-center leading-relaxed">
                AI drafts a narrative you can freely edit before publishing.
                Nothing is shared until you publish.
              </p>
            </div>
          </Card>
        </div>

        {/* Report canvas */}
        <div className="lg:col-span-2">
          {phase === 'idle' &&
          <Card>
              <EmptyState
              icon="Sparkles"
              title="Ready when you are"
              description="Choose a student and term, then generate a beautiful growth narrative in seconds." />
            
            </Card>
          }

          {phase === 'thinking' &&
          <Card className="p-10 flex flex-col items-center justify-center text-center">
              <motion.span
              className="flex h-16 w-16 items-center justify-center rounded-3xl bg-emerald-50 dark:bg-emerald-500/15 text-emerald-500 mb-5"
              animate={{
                scale: [1, 1.08, 1]
              }}
              transition={{
                repeat: Infinity,
                duration: 1.4
              }}>
              
                <SparklesIcon className="h-7 w-7" />
              </motion.span>
              <p className="font-display font-bold text-slate-800 dark:text-slate-100">
                Observing {student.name.split(' ')[0]}’s journey…
              </p>
              <p className="text-sm text-slate-400 mt-1">
                Weaving observations into a warm narrative.
              </p>
              <div className="mt-6 w-full max-w-sm space-y-2.5">
                {[0, 1, 2].map((i) =>
              <div
                key={i}
                className="h-3 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden relative">
                
                    <motion.div
                  className="absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-emerald-300/60 to-transparent"
                  animate={{
                    x: ['-100%', '300%']
                  }}
                  transition={{
                    repeat: Infinity,
                    duration: 1.3,
                    delay: i * 0.2
                  }} />
                
                  </div>
              )}
              </div>
            </Card>
          }

          {(phase === 'streaming' ||
          phase === 'ready' ||
          phase === 'published') &&
          <Card className="overflow-hidden print:shadow-none">
              {/* Report header */}
              <div className="bg-brand-600 text-white px-7 py-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <img
                    src={LOGO_URL}
                    alt=""
                    className="h-10 w-10 rounded-xl bg-white/90 p-0.5" />
                  
                    <div>
                      <p className="font-display font-extrabold text-lg leading-tight">
                        Key International School
                      </p>
                      <p className="text-brand-100 text-sm">
                        Montessori Growth Report · {term}
                      </p>
                    </div>
                  </div>
                  {phase === 'published' &&
                <Badge tone="emerald">Published</Badge>
                }
                </div>
                <div className="flex items-center gap-4 mt-6">
                  <Avatar
                  src={student.avatar}
                  name={student.name}
                  size={56}
                  className="ring-4 ring-white/30" />
                
                  <div>
                    <p className="font-display text-xl font-extrabold">
                      {student.name}
                    </p>
                    <p className="text-brand-100 text-sm">
                      {student.admissionNo} · {student.className} Class ·{' '}
                      {subject}
                    </p>
                  </div>
                </div>
              </div>

              {/* Competency chips */}
              <div className="px-7 py-5 border-b border-slate-100 dark:border-slate-800 grid grid-cols-2 sm:grid-cols-3 gap-3">
                {competencyScores.map((c) =>
              <div key={c.label}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-semibold text-slate-600 dark:text-slate-300">
                        {c.label}
                      </span>
                      <span className="text-slate-400">{c.value}</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                      <motion.div
                    className="h-full rounded-full bg-emerald-500"
                    initial={{
                      width: 0
                    }}
                    animate={{
                      width: `${c.value}%`
                    }}
                    transition={{
                      duration: 0.8
                    }} />
                  
                    </div>
                  </div>
              )}
              </div>

              {/* Sections */}
              <div className="px-7 py-6 space-y-6">
                <AnimatePresence>
                  {sections.slice(0, visibleCount).map((s) =>
                <motion.section
                  key={s.key}
                  initial={{
                    opacity: 0,
                    y: 10
                  }}
                  animate={{
                    opacity: 1,
                    y: 0
                  }}
                  transition={{
                    duration: 0.4
                  }}>
                  
                      <div className="flex items-center gap-2 mb-2">
                        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-50 dark:bg-emerald-500/15 text-emerald-600">
                          <SectionIcon name={s.icon} />
                        </span>
                        <h4 className="font-display font-bold text-slate-800 dark:text-slate-100">
                          {s.title}
                        </h4>
                      </div>
                      {editing ?
                  <textarea
                    value={s.content}
                    onChange={(e) => updateSection(s.key, e.target.value)}
                    rows={s.content.split('\n').length + 2}
                    className="w-full rounded-2xl border border-brand-200 dark:border-slate-700 bg-brand-50/40 dark:bg-slate-800 p-3 text-sm text-slate-700 dark:text-slate-200 outline-none focus:ring-2 focus:ring-brand-500/40 leading-relaxed" /> :


                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-line pl-9">
                          {s.content}
                        </p>
                  }
                    </motion.section>
                )}
                </AnimatePresence>

                {phase === 'streaming' &&
              <div className="flex items-center gap-2 text-sm text-slate-400 pl-9">
                    <Loader2Icon className="h-4 w-4 animate-spin" /> writing…
                  </div>
              }
              </div>

              {(phase === 'ready' || phase === 'published') &&
            <div className="px-7 py-5 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Avatar
                  name="Sophie Laurent"
                  size={34}
                  src={students[0].avatar} />
                
                    <div>
                      <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">
                        Sophie Laurent
                      </p>
                      <p className="text-xs text-slate-400">
                        Lead Guide · Ocean Class
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-slate-400">
                    Generated {term} · {new Date().toLocaleDateString()}
                  </p>
                </div>
            }
            </Card>
          }
        </div>
      </div>
    </div>);

}
function Field({
  label,
  children



}: {label: string;children: React.ReactNode;}) {
  return (
    <div>
      <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
        {label}
      </label>
      {children}
    </div>);

}
function Select({
  value,
  onChange,
  options




}: {value: string;onChange: (v: string) => void;options: string[];}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2.5 text-sm font-semibold text-slate-800 dark:text-slate-100 outline-none focus:ring-2 focus:ring-brand-500/40">
      
      {options.map((o) =>
      <option key={o} value={o}>
          {o}
        </option>
      )}
    </select>);

}