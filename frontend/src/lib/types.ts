export type Role = 'admin' | 'principal' | 'teacher' | 'parent' | 'student';

export interface UserProfile {
  id: string;
  name: string;
  role: Role;
  title: string;
  avatar: string;
}

export interface Student {
  id: string;
  admissionNo: string;
  name: string;
  avatar: string;
  dob: string;
  age: number;
  gender: 'Female' | 'Male';
  className: string;
  stream: string;
  house: 'Sunrise' | 'Ocean' | 'Forest' | 'Meadow';
  nationality: string;
  languages: string[];
  parent: string;
  parentPhone: string;
  medicalNotes: string;
  status: 'Enrolled' | 'Pending' | 'Alumni';
  attendance: number;
  growth: number;
}

export interface ClassRoom {
  id: string;
  name: string;
  teacher: string;
  teacherAvatar: string;
  students: number;
  ageGroup: string;
  house: string;
  color: string;
}

export interface Announcement {
  id: string;
  title: string;
  body: string;
  author: string;
  date: string;
  tag: 'Event' | 'Notice' | 'Academic' | 'Holiday';
}

export interface EventItem {
  id: string;
  title: string;
  date: string;
  time: string;
  type: 'Exam' | 'Sports' | 'Trip' | 'Meeting' | 'PTA' | 'Holiday';
}

export interface Activity {
  id: string;
  who: string;
  avatar: string;
  action: string;
  target: string;
  time: string;
}