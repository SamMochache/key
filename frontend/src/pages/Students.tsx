import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { UserPlusIcon, SearchIcon, FilterIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Avatar } from '../components/ui/Avatar';
import { students } from '../lib/data';
const statusTone = {
  Enrolled: 'emerald',
  Pending: 'warm',
  Alumni: 'slate'
} as const;
export function Students() {
  const [q, setQ] = useState('');
  const filtered = students.filter((s) =>
  (s.name + s.admissionNo + s.className).
  toLowerCase().
  includes(q.toLowerCase())
  );
  return (
    <div>
      <PageHeader
        title="Students"
        description="Every child, cared for as an individual. Browse profiles, growth, and enrolment."
        actions={
        <Button>
            <UserPlusIcon className="h-4 w-4" /> Enroll student
          </Button>
        } />
      

      <Card className="overflow-hidden">
        <div className="flex flex-col sm:flex-row items-center gap-3 p-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2 flex-1 w-full rounded-2xl bg-slate-100 dark:bg-slate-800 px-3 py-2">
            <SearchIcon className="h-4 w-4 text-slate-400" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search by name, admission no…"
              className="flex-1 bg-transparent text-sm outline-none text-slate-700 dark:text-slate-200" />
            
          </div>
          <Button variant="secondary" className="w-full sm:w-auto">
            <FilterIcon className="h-4 w-4" /> Filters
          </Button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800">
                <th className="px-5 py-3">Student</th>
                <th className="px-5 py-3 hidden md:table-cell">Class</th>
                <th className="px-5 py-3 hidden lg:table-cell">House</th>
                <th className="px-5 py-3 hidden lg:table-cell">Attendance</th>
                <th className="px-5 py-3">Growth</th>
                <th className="px-5 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {filtered.map((s) =>
              <tr
                key={s.id}
                className="group hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                
                  <td className="px-5 py-3">
                    <Link
                    to={`/students/${s.id}`}
                    className="flex items-center gap-3">
                    
                      <Avatar src={s.avatar} name={s.name} size={40} />
                      <div>
                        <p className="font-semibold text-slate-800 dark:text-slate-100 group-hover:text-brand-600">
                          {s.name}
                        </p>
                        <p className="text-xs text-slate-400">
                          {s.admissionNo} · Age {s.age}
                        </p>
                      </div>
                    </Link>
                  </td>
                  <td className="px-5 py-3 hidden md:table-cell text-slate-600 dark:text-slate-300">
                    {s.className}
                  </td>
                  <td className="px-5 py-3 hidden lg:table-cell text-slate-600 dark:text-slate-300">
                    {s.house}
                  </td>
                  <td className="px-5 py-3 hidden lg:table-cell">
                    {s.status === 'Enrolled' ?
                  <span className="font-semibold text-slate-700 dark:text-slate-200">
                        {s.attendance}%
                      </span> :

                  <span className="text-slate-300">—</span>
                  }
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2 w-28">
                      <div className="flex-1 h-1.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                        <div
                        className="h-full rounded-full bg-emerald-500"
                        style={{
                          width: `${s.growth}%`
                        }} />
                      
                      </div>
                      <span className="text-xs font-semibold text-slate-500">
                        {s.growth || '—'}
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <Badge tone={statusTone[s.status]}>{s.status}</Badge>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>);

}