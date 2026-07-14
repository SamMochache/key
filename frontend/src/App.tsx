import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { Layout } from './components/shell/Layout';
import { Dashboard } from './pages/Dashboard';
import { Students } from './pages/Students';
import { StudentProfile } from './pages/StudentProfile';
import { Classes } from './pages/Classes';
import { Attendance } from './pages/Attendance';
import { Academics } from './pages/Academics';
import { Assessments } from './pages/Assessments';
import { AIReports } from './pages/AIReports';
import { Portfolio } from './pages/Portfolio';
import { Calendar } from './pages/Calendar';
import { Communication } from './pages/Communication';
import { Analytics } from './pages/Analytics';
import { Reports } from './pages/Reports';
export function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/students" element={<Students />} />
            <Route path="/students/:id" element={<StudentProfile />} />
            <Route path="/classes" element={<Classes />} />
            <Route path="/attendance" element={<Attendance />} />
            <Route path="/academics" element={<Academics />} />
            <Route path="/assessments" element={<Assessments />} />
            <Route path="/ai-reports" element={<AIReports />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/communication" element={<Communication />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="*" element={<Dashboard />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>);

}