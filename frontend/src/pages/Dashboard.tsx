import React, { useEffect, useState } from 'react';
import { useApp } from '../context/AppContext';
import { PROFILES } from '../lib/data';
import { getAccessToken, getCurrentUser, getDashboardSummary, type DashboardSummary } from '../lib/api';
import { AdminDashboard } from '../components/dashboards/AdminDashboard';
import { PrincipalDashboard } from '../components/dashboards/PrincipalDashboard';
import { TeacherDashboard } from '../components/dashboards/TeacherDashboard';
import { ParentDashboard } from '../components/dashboards/ParentDashboard';
import { StudentDashboard } from '../components/dashboards/StudentDashboard';

export function Dashboard() {
  const { role } = useApp();
  const [name, setName] = useState(PROFILES[role].name);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);

  useEffect(() => {
    if (!getAccessToken()) return;

    let active = true;
    Promise.all([getCurrentUser(), getDashboardSummary()])
      .then(([user, dashboardSummary]) => {
        if (!active) return;
        if (user.full_name) setName(user.full_name);
        setSummary(dashboardSummary ?? null);
      })
      .catch(() => {
        // Keep the existing prototype identity/data when the API is unavailable.
      });

    return () => {
      active = false;
    };
  }, []);

  switch (role) {
    case 'admin':
      return <AdminDashboard name={name} summary={summary} />;
    case 'principal':
      return <PrincipalDashboard name={name} />;
    case 'teacher':
      return <TeacherDashboard name={name} />;
    case 'parent':
      return <ParentDashboard name={name} />;
    case 'student':
      return <StudentDashboard name={name} />;
    default:
      return <AdminDashboard name={name} summary={summary} />;
  }
}
