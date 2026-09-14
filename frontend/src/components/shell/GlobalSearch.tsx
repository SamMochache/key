import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  SearchIcon,
  UsersIcon,
  SchoolIcon,
  FileTextIcon,
  BookOpenIcon,
  CornerDownLeftIcon,
  Loader2Icon,
} from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { listClassrooms, listStudents, listSubjects, listTeachers, type ApiClassroom, type ApiStudent, type ApiSubject, type ApiTeacher } from '../../lib/api';
import { Avatar } from '../ui/Avatar';

interface Result {
  type: string;
  label: string;
  sub: string;
  to: string;
  icon: React.ReactNode;
  avatar?: string;
}

export function GlobalSearch() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState('');
  const [students, setStudents] = useState<ApiStudent[]>([]);
  const [teachers, setTeachers] = useState<ApiTeacher[]>([]);
  const [classrooms, setClassrooms] = useState<ApiClassroom[]>([]);
  const [subjects, setSubjects] = useState<ApiSubject[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setOpen(true);
      }
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  useEffect(() => {
    if (!open) {
      setQ('');
      return;
    }

    const focusTimer = window.setTimeout(() => inputRef.current?.focus(), 50);
    let cancelled = false;

    setLoading(true);
    setError('');

    Promise.all([
      listStudents({ search: q.trim() || undefined }),
      listTeachers({ search: q.trim() || undefined }),
      listClassrooms({ search: q.trim() || undefined }),
      listSubjects({ search: q.trim() || undefined, active: true }),
    ])
      .then(([studentResults, teacherResults, classroomResults, subjectResults]) => {
        if (cancelled) return;
        setStudents(studentResults);
        setTeachers(teacherResults);
        setClassrooms(classroomResults);
        setSubjects(subjectResults);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Unable to search school data.');
        setStudents([]);
        setTeachers([]);
        setClassrooms([]);
        setSubjects([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
      window.clearTimeout(focusTimer);
    };
  }, [open, q]);

  const results = useMemo<Result[]>(() => {
    const term = q.trim().toLowerCase();

    const base: Result[] = [
      ...students.map((s) => ({
        type: 'Student',
        label: s.full_name,
        sub: `${s.admission_number} · ${s.school_name}`,
        to: `/students/${s.id}`,
        icon: <UsersIcon className="h-4 w-4" />,
      })),
      ...teachers.map((t) => ({
        type: 'Teacher',
        label: t.full_name,
        sub: `${t.employee_number || 'Teacher'} · ${t.department_name || 'Teaching staff'}`,
        to: `/teachers/${t.id}`,
        icon: <UsersIcon className="h-4 w-4" />,
      })),
      ...classrooms.map((c) => ({
        type: 'Class',
        label: c.name,
        sub: `${c.primary_teacher_name || 'No primary teacher'} · ${c.student_count} students`,
        to: '/classes',
        icon: <SchoolIcon className="h-4 w-4" />,
      })),
      ...subjects.map((s) => ({
        type: 'Subject',
        label: s.name,
        sub: `${s.code} · ${s.curriculum_name}`,
        to: '/academics',
        icon: <BookOpenIcon className="h-4 w-4" />,
      })),
      {
        type: 'Report',
        label: 'AI Narrative Reports',
        sub: 'Generate & publish',
        to: '/ai-reports',
        icon: <FileTextIcon className="h-4 w-4" />,
      },
    ];

    if (!term) return base.slice(0, 8);

    return base
      .filter((r) => (r.label + r.sub + r.type).toLowerCase().includes(term))
      .slice(0, 8);
  }, [q, students, teachers, classrooms, subjects]);

  const go = (to: string) => {
    setOpen(false);
    navigate(to);
  };

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 rounded-2xl bg-slate-100 dark:bg-slate-800 px-3 py-2 text-sm text-slate-400 dark:text-slate-500 hover:bg-slate-200/70 dark:hover:bg-slate-700 transition-colors w-full max-w-xs"
        aria-label="Open global search"
      >
        <SearchIcon className="h-4 w-4" />
        <span className="hidden sm:inline">Search students, teachers, classes…</span>
        <span className="hidden md:inline ml-auto text-[11px] font-semibold rounded-md bg-white dark:bg-slate-900 px-1.5 py-0.5 border border-slate-200 dark:border-slate-700">
          ⌘K
        </span>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-[12vh] bg-slate-900/40 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setOpen(false)}
          >
            <motion.div
              className="w-full max-w-xl rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-softlg overflow-hidden"
              initial={{ opacity: 0, y: -12, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -12, scale: 0.98 }}
              transition={{ type: 'spring', stiffness: 400, damping: 30 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center gap-3 px-5 border-b border-slate-100 dark:border-slate-800">
                <SearchIcon className="h-5 w-5 text-slate-400" />
                <input
                  ref={inputRef}
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="Search students, teachers, classes, subjects…"
                  className="flex-1 bg-transparent py-4 text-slate-800 dark:text-slate-100 outline-none placeholder:text-slate-400"
                  autoComplete="off"
                />
                {loading && <Loader2Icon className="h-4 w-4 animate-spin text-brand-600" />}
              </div>

              <div className="max-h-80 overflow-y-auto p-2">
                {error ? (
                  <div className="py-8 px-4 text-center text-sm text-rose-600">{error}</div>
                ) : loading && results.length === 0 ? (
                  <div className="py-10 flex justify-center text-slate-400">
                    <Loader2Icon className="h-5 w-5 animate-spin" />
                  </div>
                ) : results.length === 0 ? (
                  <div className="py-10 text-center text-sm text-slate-400">
                    {q.trim() ? `No matches for “${q}”.` : 'No searchable records found.'}
                  </div>
                ) : (
                  results.map((r, i) => (
                    <button
                      key={`${r.type}-${r.to}-${i}`}
                      onClick={() => go(r.to)}
                      className="w-full flex items-center gap-3 rounded-2xl px-3 py-2.5 hover:bg-slate-100 dark:hover:bg-slate-800 text-left transition-colors"
                    >
                      {r.avatar ? (
                        <Avatar src={r.avatar} name={r.label} size={32} />
                      ) : (
                        <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-brand-50 dark:bg-slate-800 text-brand-600 dark:text-brand-300">
                          {r.icon}
                        </span>
                      )}
                      <span className="flex-1 min-w-0">
                        <span className="block text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">
                          {r.label}
                        </span>
                        <span className="block text-xs text-slate-400 truncate">
                          {r.sub}
                        </span>
                      </span>
                      <span className="text-[11px] font-semibold text-slate-400">{r.type}</span>
                    </button>
                  ))
                )}
              </div>

              <div className="flex items-center gap-2 px-5 py-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400">
                <CornerDownLeftIcon className="h-3.5 w-3.5" /> to open · Esc to close
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
