import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Layout } from './components/shell/Layout';
import { Dashboard } from './pages/Dashboard';
import { Login } from './pages/Login';
import { Students } from './pages/Students';
import { StudentProfile } from './pages/StudentProfile';
import { Teachers } from './pages/Teachers';
import { Classes } from './pages/Classes';
import { ClassProfile } from './pages/ClassProfile';
import { Attendance } from './pages/Attendance';
import { Academics } from './pages/Academics';
import { Lessons } from './pages/Lessons';
import { Timetables } from './pages/Timetables';
import { Assessments } from './pages/Assessments';
import { Evidence } from './pages/Evidence';
import { AIReports } from './pages/AIReports';
import { StudentAIReports } from './pages/StudentAIReports';
import { ParentAIReports } from './pages/ParentAIReports';
import { Parents } from './pages/Parents';
import { Portfolio } from './pages/Portfolio';
import { Calendar } from './pages/Calendar';
import { Communication } from './pages/Communication';
import { Analytics } from './pages/Analytics';
import { Reports } from './pages/Reports';

const STAFF = ['admin', 'teacher'] as const;
const PEOPLE = ['admin', 'teacher'] as const;
const LEARNING = ['admin', 'teacher', 'student'] as const;
const ALL = ['admin', 'teacher', 'student'] as const;
const STUDENT = ['student'] as const;
const PARENT = ['parent'] as const;

export function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/forbidden" element={<Forbidden />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route element={<ProtectedRoute roles={[...PEOPLE]} />}>
                <Route path="/students" element={<Students />} />
                <Route path="/students/:id" element={<StudentProfile />} />
                <Route path="/teachers" element={<Teachers />} />
                <Route path="/classes" element={<Classes />} />
                <Route path="/classes/:id" element={<ClassProfile />} />
              </Route>
              <Route element={<ProtectedRoute roles={[...STAFF]} />}>
                <Route path="/attendance" element={<Attendance />} />
                <Route path="/lessons" element={<Lessons />} />
                <Route path="/timetables" element={<Timetables />} />
                <Route path="/assessments" element={<Assessments />} />
                <Route path="/ai-reports" element={<AIReports />} />
                <Route path="/parents" element={<Parents />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/reports" element={<Reports />} />
              </Route>
              <Route element={<ProtectedRoute roles={[...LEARNING]} />}>
                <Route path="/academics" element={<Academics />} />
                <Route path="/evidence" element={<Evidence />} />
              </Route>
              <Route element={<ProtectedRoute roles={[...ALL]} />}>
                <Route path="/portfolio" element={<Portfolio />} />
                <Route path="/calendar" element={<Calendar />} />
                <Route path="/communication" element={<Communication />} />
              </Route>
              <Route element={<ProtectedRoute roles={[...STUDENT]} />}>
                <Route path="/my-ai-reports" element={<StudentAIReports />} />
              </Route>
              <Route element={<ProtectedRoute roles={[...PARENT]} />}>
                <Route path="/learner-reports" element={<ParentAIReports />} />
              </Route>
              <Route path="*" element={<Dashboard />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}

function Forbidden() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 px-4">
      <div className="max-w-md text-center">
        <p className="text-sm font-bold uppercase tracking-wider text-rose-600">403</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900 dark:text-slate-100">Access denied</h1>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Your account does not have permission to view this page.</p>
        <a href="/" className="inline-block mt-6 rounded-2xl bg-brand-600 px-5 py-3 text-sm font-bold text-white">Return to dashboard</a>
      </div>
    </main>
  );
}
