import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { Breadcrumbs } from './Breadcrumbs';
export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div className="min-h-full bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="lg:pl-72 flex flex-col min-h-screen">
        <Topbar onMenu={() => setSidebarOpen(true)} />
        <div className="px-4 lg:px-8 pt-5 no-print">
          <Breadcrumbs />
        </div>
        <main className="flex-1 px-4 lg:px-8 py-6">
          <Outlet />
        </main>
      </div>
    </div>);

}