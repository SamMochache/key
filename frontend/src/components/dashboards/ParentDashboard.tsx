import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { MessageSquareIcon, ArrowRightIcon, UsersIcon } from 'lucide-react';
import { PageHeader } from '../ui/PageHeader';
import { Card, CardHeader } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Avatar } from '../ui/Avatar';
import { listMyChildren, type ParentChild } from '../../lib/parentApi';

export function ParentDashboard({ name }: { name: string }) {
  const [children, setChildren] = useState<ParentChild[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    listMyChildren()
      .then(setChildren)
      .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load linked learners.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader
        title="Your family dashboard"
        description={`Welcome, ${name}. This view shows only learners linked to your parent account.`}
        actions={
          <Link to="/communication" className="inline-flex items-center gap-2 rounded-2xl bg-brand-600 text-white px-4 py-2.5 text-sm font-semibold hover:bg-brand-700">
            <MessageSquareIcon className="h-4 w-4" /> Message guide
          </Link>
        }
      />

      {error && <div className="mb-5 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      {loading ? (
        <Card className="p-8 text-sm text-slate-500">Loading your linked learners…</Card>
      ) : children.length === 0 ? (
        <Card className="p-10 text-center">
          <UsersIcon className="mx-auto h-10 w-10 text-slate-300" />
          <h2 className="mt-4 font-display text-lg font-extrabold text-slate-900 dark:text-white">No learners linked yet</h2>
          <p className="mt-2 text-sm text-slate-500">Ask your school administrator to link your parent account to a learner.</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {children.map((child) => (
            <Card key={child.id} className="overflow-hidden">
              <div className="p-5">
                <div className="flex items-start gap-4">
                  <Avatar src={child.profile_photo || undefined} name={child.full_name} size={64} ring />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h2 className="font-display text-xl font-extrabold text-slate-900 dark:text-white">{child.full_name}</h2>
                      <Badge tone="brand">{child.classroom?.name || 'Not enrolled'}</Badge>
                    </div>
                    <p className="text-sm text-slate-400 mt-1">{child.admission_number} · {child.school_name}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-6">
                  <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-4">
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Attendance</p>
                    <p className="mt-1 text-2xl font-extrabold text-emerald-600">{child.attendance_rate == null ? '—' : `${child.attendance_rate}%`}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-4">
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Growth index</p>
                    <p className="mt-1 text-2xl font-extrabold text-brand-600">{child.growth_index == null ? '—' : child.growth_index}</p>
                  </div>
                </div>
              </div>

              <div className="border-t border-slate-100 dark:border-slate-800 p-5">
                <CardHeader
                  title="Latest portfolio"
                  subtitle={child.latest_portfolio ? `Added ${child.latest_portfolio.event_date || 'recently'}` : 'No portfolio evidence yet'}
                  action={child.can_view_reports ? <Link to="/learner-reports" className="text-sm font-bold text-brand-600 inline-flex items-center gap-1">Reports <ArrowRightIcon className="h-3.5 w-3.5" /></Link> : null}
                />
                {child.latest_portfolio ? (
                  <div className="mt-3 rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-4">
                    <p className="font-semibold text-slate-800 dark:text-slate-100">{child.latest_portfolio.title}</p>
                    {child.latest_portfolio.description && <p className="mt-1 text-sm text-slate-500">{child.latest_portfolio.description}</p>}
                  </div>
                ) : (
                  <p className="mt-3 text-sm text-slate-500">Portfolio evidence will appear here when the school publishes it.</p>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
