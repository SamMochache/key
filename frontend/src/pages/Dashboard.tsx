import React from 'react';
import { useApp } from '../context/AppContext';
import { PROFILES } from '../lib/data';
import { AdminDashboard } from '../components/dashboards/AdminDashboard';
import { PrincipalDashboard } from '../components/dashboards/PrincipalDashboard';
import { TeacherDashboard } from '../components/dashboards/TeacherDashboard';
import { ParentDashboard } from '../components/dashboards/ParentDashboard';
import { StudentDashboard } from '../components/dashboards/StudentDashboard';
export function Dashboard() {
  const { role } = useApp();
  const name = PROFILES[role].name;
  switch (role) {
    case 'admin':
      return <AdminDashboard name={name} />;
    case 'principal':
      return <PrincipalDashboard name={name} />;
    case 'teacher':
      return <TeacherDashboard name={name} />;
    case 'parent':
      return <ParentDashboard name={name} />;
    case 'student':
      return <StudentDashboard name={name} />;
    default:
      return <AdminDashboard name={name} />;
  }
}