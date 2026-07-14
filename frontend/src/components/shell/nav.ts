import type { Role } from '../../lib/types';

export interface NavItem {
  label: string;
  to: string;
  icon: string;
  roles: Role[];
}

export interface NavGroup {
  title: string;
  items: NavItem[];
}

const ALL: Role[] = ['admin', 'principal', 'teacher', 'parent', 'student'];

export const navGroups: NavGroup[] = [
{
  title: 'Overview',
  items: [
  { label: 'Dashboard', to: '/', icon: 'LayoutDashboard', roles: ALL }]

},
{
  title: 'People',
  items: [
  {
    label: 'Students',
    to: '/students',
    icon: 'Users',
    roles: ['admin', 'principal', 'teacher']
  },
  {
    label: 'Classes',
    to: '/classes',
    icon: 'School',
    roles: ['admin', 'principal', 'teacher']
  },
  {
    label: 'Attendance',
    to: '/attendance',
    icon: 'CalendarCheck',
    roles: ['admin', 'principal', 'teacher', 'parent']
  }]

},
{
  title: 'Learning',
  items: [
  {
    label: 'Academics',
    to: '/academics',
    icon: 'BookOpen',
    roles: ['admin', 'principal', 'teacher', 'student']
  },
  {
    label: 'Assessments',
    to: '/assessments',
    icon: 'ClipboardCheck',
    roles: ['admin', 'principal', 'teacher', 'parent']
  },
  {
    label: 'AI Reports',
    to: '/ai-reports',
    icon: 'Sparkles',
    roles: ['admin', 'principal', 'teacher', 'parent']
  },
  { label: 'Portfolio', to: '/portfolio', icon: 'FolderHeart', roles: ALL }]

},
{
  title: 'School Life',
  items: [
  { label: 'Calendar', to: '/calendar', icon: 'CalendarDays', roles: ALL },
  {
    label: 'Communication',
    to: '/communication',
    icon: 'MessagesSquare',
    roles: ALL
  },
  {
    label: 'Analytics',
    to: '/analytics',
    icon: 'TrendingUp',
    roles: ['admin', 'principal', 'teacher']
  },
  {
    label: 'Reports',
    to: '/reports',
    icon: 'FileBarChart',
    roles: ['admin', 'principal', 'teacher']
  }]

}];