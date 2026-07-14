import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRightIcon, HomeIcon } from 'lucide-react';
const LABELS: Record<string, string> = {
  students: 'Students',
  classes: 'Classes',
  attendance: 'Attendance',
  academics: 'Academics',
  assessments: 'Assessments',
  'ai-reports': 'AI Reports',
  portfolio: 'Portfolio',
  calendar: 'Calendar',
  communication: 'Communication',
  analytics: 'Analytics',
  reports: 'Reports'
};
export function Breadcrumbs() {
  const { pathname } = useLocation();
  const parts = pathname.split('/').filter(Boolean);
  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm">
      <Link
        to="/"
        className="flex items-center gap-1.5 text-slate-400 hover:text-brand-600 font-medium">
        
        <HomeIcon className="h-4 w-4" />
        Home
      </Link>
      {parts.map((p, i) => {
        const path = '/' + parts.slice(0, i + 1).join('/');
        const isLast = i === parts.length - 1;
        const label = LABELS[p] ?? p.charAt(0).toUpperCase() + p.slice(1);
        return (
          <span key={path} className="flex items-center gap-1.5">
            <ChevronRightIcon className="h-4 w-4 text-slate-300 dark:text-slate-600" />
            {isLast ?
            <span className="font-semibold text-slate-700 dark:text-slate-200">
                {label}
              </span> :

            <Link
              to={path}
              className="text-slate-400 hover:text-brand-600 font-medium">
              
                {label}
              </Link>
            }
          </span>);

      })}
    </nav>);

}