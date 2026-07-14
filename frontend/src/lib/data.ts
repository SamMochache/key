import type {
  Student,
  ClassRoom,
  Announcement,
  EventItem,
  Activity,
  UserProfile,
  Role } from
'./types';

const CHILD1 = "/f9edb2ba-144c-4c89-9fc6-3d2d089fd2d8.jpg";

const CHILD2 = "/f421f384-726a-48a2-b7fa-e666c3e2cbb7.jpg";

const TEACHER1 = "/6834941f-4606-43a0-adae-d2860bf30bed.jpg";


export const LOGO_URL = "/3db427c4-c7b0-470f-b12e-e68d47b7e36e.jpg";

export const PORTFOLIO_IMG = "/a87f13eb-1191-4e50-91d5-f123e2a65143.jpg";


export const PROFILES: Record<Role, UserProfile> = {
  admin: {
    id: 'u1',
    name: 'Amara Okafor',
    role: 'admin',
    title: 'School Administrator',
    avatar: TEACHER1
  },
  principal: {
    id: 'u2',
    name: 'Dr. Elena Rossi',
    role: 'principal',
    title: 'Principal',
    avatar: TEACHER1
  },
  teacher: {
    id: 'u3',
    name: 'Sophie Laurent',
    role: 'teacher',
    title: 'Lead Guide · Ocean Class',
    avatar: TEACHER1
  },
  parent: {
    id: 'u4',
    name: 'David Chen',
    role: 'parent',
    title: 'Parent of Mia Chen',
    avatar: TEACHER1
  },
  student: {
    id: 'u5',
    name: 'Mia Chen',
    role: 'student',
    title: 'Ocean Class · Age 7',
    avatar: CHILD2
  }
};

export const ROLE_LABELS: Record<Role, string> = {
  admin: 'Administrator',
  principal: 'Principal',
  teacher: 'Teacher',
  parent: 'Parent',
  student: 'Student'
};

export const students: Student[] = [
{
  id: 's1',
  admissionNo: 'KIS-2419',
  name: 'Mia Chen',
  avatar: CHILD2,
  dob: '2018-04-12',
  age: 7,
  gender: 'Female',
  className: 'Ocean',
  stream: 'Lower Elementary',
  house: 'Ocean',
  nationality: 'Singaporean',
  languages: ['English', 'Mandarin'],
  parent: 'David Chen',
  parentPhone: '+65 8123 4567',
  medicalNotes: 'Mild peanut allergy',
  status: 'Enrolled',
  attendance: 96,
  growth: 88
},
{
  id: 's2',
  admissionNo: 'KIS-2402',
  name: 'Noah Bennett',
  avatar: CHILD1,
  dob: '2017-09-03',
  age: 8,
  gender: 'Male',
  className: 'Forest',
  stream: 'Lower Elementary',
  house: 'Forest',
  nationality: 'British',
  languages: ['English', 'French'],
  parent: 'Laura Bennett',
  parentPhone: '+44 7700 900123',
  medicalNotes: 'None',
  status: 'Enrolled',
  attendance: 92,
  growth: 81
},
{
  id: 's3',
  admissionNo: 'KIS-2455',
  name: 'Aria Kapoor',
  avatar: CHILD2,
  dob: '2019-01-22',
  age: 6,
  gender: 'Female',
  className: 'Meadow',
  stream: 'Casa',
  house: 'Meadow',
  nationality: 'Indian',
  languages: ['English', 'Hindi'],
  parent: 'Rohan Kapoor',
  parentPhone: '+91 98200 11223',
  medicalNotes: 'Asthma — inhaler on file',
  status: 'Enrolled',
  attendance: 98,
  growth: 94
},
{
  id: 's4',
  admissionNo: 'KIS-2388',
  name: 'Liam O’Connor',
  avatar: CHILD1,
  dob: '2016-11-30',
  age: 9,
  gender: 'Male',
  className: 'Sunrise',
  stream: 'Upper Elementary',
  house: 'Sunrise',
  nationality: 'Irish',
  languages: ['English'],
  parent: 'Fiona O’Connor',
  parentPhone: '+353 87 123 4567',
  medicalNotes: 'None',
  status: 'Enrolled',
  attendance: 89,
  growth: 76
},
{
  id: 's5',
  admissionNo: 'KIS-2471',
  name: 'Yuki Tanaka',
  avatar: CHILD2,
  dob: '2018-07-18',
  age: 7,
  gender: 'Female',
  className: 'Ocean',
  stream: 'Lower Elementary',
  house: 'Ocean',
  nationality: 'Japanese',
  languages: ['English', 'Japanese'],
  parent: 'Haruto Tanaka',
  parentPhone: '+81 90 1234 5678',
  medicalNotes: 'None',
  status: 'Enrolled',
  attendance: 94,
  growth: 90
},
{
  id: 's6',
  admissionNo: 'KIS-2500',
  name: 'Sofia Alvarez',
  avatar: CHILD2,
  dob: '2019-03-09',
  age: 6,
  gender: 'Female',
  className: 'Meadow',
  stream: 'Casa',
  house: 'Meadow',
  nationality: 'Spanish',
  languages: ['English', 'Spanish'],
  parent: 'Carmen Alvarez',
  parentPhone: '+34 612 345 678',
  medicalNotes: 'None',
  status: 'Pending',
  attendance: 0,
  growth: 0
}];


export const classes: ClassRoom[] = [
{
  id: 'c1',
  name: 'Ocean',
  teacher: 'Sophie Laurent',
  teacherAvatar: TEACHER1,
  students: 22,
  ageGroup: '6–9 yrs',
  house: 'Ocean',
  color: 'brand'
},
{
  id: 'c2',
  name: 'Forest',
  teacher: 'Marcus Reed',
  teacherAvatar: TEACHER1,
  students: 20,
  ageGroup: '6–9 yrs',
  house: 'Forest',
  color: 'emerald'
},
{
  id: 'c3',
  name: 'Meadow',
  teacher: 'Priya Nair',
  teacherAvatar: TEACHER1,
  students: 18,
  ageGroup: '3–6 yrs',
  house: 'Meadow',
  color: 'warm'
},
{
  id: 'c4',
  name: 'Sunrise',
  teacher: 'James Whitmore',
  teacherAvatar: TEACHER1,
  students: 24,
  ageGroup: '9–12 yrs',
  house: 'Sunrise',
  color: 'brand'
}];


export const announcements: Announcement[] = [
{
  id: 'a1',
  title: 'Spring Nature Walk — permission slips due',
  body: 'Ocean and Forest classes will visit the botanical gardens on Friday. Please return signed slips.',
  author: 'Sophie Laurent',
  date: '2h ago',
  tag: 'Event'
},
{
  id: 'a2',
  title: 'Parent–Guide Conferences open for booking',
  body: 'Term 2 conferences are now available. Book your 20-minute slot through the Parent Portal.',
  author: 'Front Office',
  date: '1d ago',
  tag: 'Notice'
},
{
  id: 'a3',
  title: 'New practical life materials in Meadow',
  body: 'We have introduced new pouring and threading works to support fine-motor development.',
  author: 'Priya Nair',
  date: '2d ago',
  tag: 'Academic'
},
{
  id: 'a4',
  title: 'School closed — Founders’ Day',
  body: 'The school will be closed on the 21st in observance of Founders’ Day.',
  author: 'Administration',
  date: '3d ago',
  tag: 'Holiday'
}];


export const events: EventItem[] = [
{
  id: 'e1',
  title: 'Term 2 Assessments Begin',
  date: 'Jul 16',
  time: '09:00',
  type: 'Exam'
},
{
  id: 'e2',
  title: 'Inter-House Sports Day',
  date: 'Jul 19',
  time: '08:30',
  type: 'Sports'
},
{
  id: 'e3',
  title: 'Botanical Gardens Trip',
  date: 'Jul 17',
  time: '10:00',
  type: 'Trip'
},
{
  id: 'e4',
  title: 'PTA Monthly Meeting',
  date: 'Jul 22',
  time: '17:30',
  type: 'PTA'
},
{
  id: 'e5',
  title: 'Parent–Guide Conferences',
  date: 'Jul 24',
  time: '14:00',
  type: 'Meeting'
}];


export const activities: Activity[] = [
{
  id: 'ac1',
  who: 'Sophie Laurent',
  avatar: TEACHER1,
  action: 'published an AI report for',
  target: 'Mia Chen',
  time: '12m ago'
},
{
  id: 'ac2',
  who: 'Priya Nair',
  avatar: TEACHER1,
  action: 'marked attendance for',
  target: 'Meadow Class',
  time: '40m ago'
},
{
  id: 'ac3',
  who: 'Front Office',
  avatar: TEACHER1,
  action: 'enrolled a new student',
  target: 'Sofia Alvarez',
  time: '1h ago'
},
{
  id: 'ac4',
  who: 'Marcus Reed',
  avatar: TEACHER1,
  action: 'added a portfolio entry for',
  target: 'Noah Bennett',
  time: '3h ago'
}];


export const attendanceTrend = [
{ month: 'Feb', rate: 93 },
{ month: 'Mar', rate: 95 },
{ month: 'Apr', rate: 92 },
{ month: 'May', rate: 96 },
{ month: 'Jun', rate: 94 },
{ month: 'Jul', rate: 97 }];


export const growthTrend = [
{ term: 'T1', practical: 62, language: 55, math: 58, culture: 60 },
{ term: 'T2', practical: 71, language: 64, math: 66, culture: 68 },
{ term: 'T3', practical: 78, language: 73, math: 74, culture: 76 },
{ term: 'T4', practical: 86, language: 82, math: 80, culture: 85 }];


export const competencyRadar = [
{ skill: 'Communication', value: 82 },
{ skill: 'Creativity', value: 90 },
{ skill: 'Critical Thinking', value: 74 },
{ skill: 'Social Skills', value: 88 },
{ skill: 'Leadership', value: 70 },
{ skill: 'Focus', value: 85 }];


export const classCompare = [
{ name: 'Ocean', growth: 88, attendance: 96 },
{ name: 'Forest', growth: 81, attendance: 92 },
{ name: 'Meadow', growth: 94, attendance: 98 },
{ name: 'Sunrise', growth: 76, attendance: 89 }];


export const assignments = [
{
  id: 'as1',
  title: 'Nature Journal — Leaf Study',
  subject: 'Culture',
  className: 'Ocean',
  due: 'Jul 18',
  status: 'Grading',
  submitted: 18,
  total: 22
},
{
  id: 'as2',
  title: 'Golden Beads — Addition',
  subject: 'Mathematics',
  className: 'Meadow',
  due: 'Jul 16',
  status: 'Open',
  submitted: 9,
  total: 18
},
{
  id: 'as3',
  title: 'Story Sequencing Cards',
  subject: 'Language',
  className: 'Forest',
  due: 'Jul 20',
  status: 'Open',
  submitted: 5,
  total: 20
},
{
  id: 'as4',
  title: 'Continents Map Work',
  subject: 'Geography',
  className: 'Sunrise',
  due: 'Jul 15',
  status: 'Grading',
  submitted: 24,
  total: 24
}];


export const subjects = [
{
  id: 'sub1',
  name: 'Practical Life',
  icon: 'Sprout',
  lessons: 24,
  color: 'emerald'
},
{ id: 'sub2', name: 'Sensorial', icon: 'Shapes', lessons: 18, color: 'warm' },
{
  id: 'sub3',
  name: 'Language',
  icon: 'BookOpen',
  lessons: 32,
  color: 'brand'
},
{
  id: 'sub4',
  name: 'Mathematics',
  icon: 'Calculator',
  lessons: 28,
  color: 'brand'
},
{
  id: 'sub5',
  name: 'Culture & Science',
  icon: 'Globe',
  lessons: 21,
  color: 'emerald'
},
{
  id: 'sub6',
  name: 'Arts & Creativity',
  icon: 'Palette',
  lessons: 15,
  color: 'warm'
}];