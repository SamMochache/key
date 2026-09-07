import type { Role } from '../../lib/types';

export interface NavItem { label: string; to: string; icon: string; roles: Role[]; }
export interface NavGroup { title: string; items: NavItem[]; }
const ALL: Role[] = ['admin', 'teacher', 'student', 'parent'];
export const navGroups: NavGroup[] = [
  { title: 'Overview', items: [{ label: 'Dashboard', to: '/', icon: 'LayoutDashboard', roles: ALL }] },
  { title: 'People', items: [
    { label: 'Students', to: '/students', icon: 'Users', roles: ['admin', 'teacher'] },
    { label: 'Teachers', to: '/teachers', icon: 'UsersRound', roles: ['admin', 'teacher'] },
    { label: 'Parents & Guardians', to: '/parents', icon: 'UserRoundCheck', roles: ['admin', 'teacher'] },
    { label: 'Classes', to: '/classes', icon: 'School', roles: ['admin', 'teacher'] },
    { label: 'Attendance', to: '/attendance', icon: 'CalendarCheck', roles: ['admin', 'teacher'] }
  ] },
  { title: 'Learning', items: [
    { label: 'Academics', to: '/academics', icon: 'BookOpen', roles: ['admin', 'teacher', 'student'] },
    { label: 'Lessons', to: '/lessons', icon: 'BookOpenCheck', roles: ['admin', 'teacher'] },
    { label: 'Assessments', to: '/assessments', icon: 'ClipboardCheck', roles: ['admin', 'teacher'] },
    { label: 'Evidence', to: '/evidence', icon: 'Files', roles: ALL },
    { label: 'AI Reports', to: '/ai-reports', icon: 'Sparkles', roles: ['admin', 'teacher'] },
    { label: 'My AI Reports', to: '/my-ai-reports', icon: 'FileText', roles: ['student'] },
    { label: 'Learner Reports', to: '/learner-reports', icon: 'FileText', roles: ['parent'] },
    { label: 'Portfolio', to: '/portfolio', icon: 'FolderHeart', roles: ALL }
  ] },
  { title: 'School Life', items: [
    { label: 'Calendar', to: '/calendar', icon: 'CalendarDays', roles: ALL },
    { label: 'Communication', to: '/communication', icon: 'MessagesSquare', roles: ALL },
    { label: 'Analytics', to: '/analytics', icon: 'TrendingUp', roles: ['admin', 'teacher'] },
    { label: 'Reports', to: '/reports', icon: 'FileBarChart', roles: ['admin', 'teacher'] }
  ] }
];
