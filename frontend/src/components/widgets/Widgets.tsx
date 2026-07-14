import React from 'react';
import {
  MegaphoneIcon,
  CalendarIcon,
  TrophyIcon,
  MedalIcon,
  GraduationCapIcon,
  MapPinIcon,
  UsersIcon } from
'lucide-react';
import { Card, CardHeader } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Avatar } from '../ui/Avatar';
import { announcements, events, activities } from '../../lib/data';
import type { EventItem } from '../../lib/types';
const tagTone: Record<string, 'brand' | 'emerald' | 'warm' | 'slate'> = {
  Event: 'brand',
  Academic: 'emerald',
  Notice: 'warm',
  Holiday: 'slate'
};
const eventStyle: Record<
  EventItem['type'],
  {
    tone: 'brand' | 'emerald' | 'warm' | 'rose' | 'slate';
    icon: React.ReactNode;
  }> =
{
  Exam: {
    tone: 'rose',
    icon: <GraduationCapIcon className="h-4 w-4" />
  },
  Sports: {
    tone: 'emerald',
    icon: <TrophyIcon className="h-4 w-4" />
  },
  Trip: {
    tone: 'warm',
    icon: <MapPinIcon className="h-4 w-4" />
  },
  Meeting: {
    tone: 'brand',
    icon: <UsersIcon className="h-4 w-4" />
  },
  PTA: {
    tone: 'slate',
    icon: <UsersIcon className="h-4 w-4" />
  },
  Holiday: {
    tone: 'slate',
    icon: <CalendarIcon className="h-4 w-4" />
  }
};
const eventToneClass = {
  brand: 'bg-brand-50 text-brand-600 dark:bg-brand-600/20 dark:text-brand-300',
  emerald:
  'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-300',
  warm: 'bg-warm-50 text-warm-600 dark:bg-warm-500/20 dark:text-warm-300',
  rose: 'bg-rose-50 text-rose-600 dark:bg-rose-500/20 dark:text-rose-300',
  slate: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
};
export function AnnouncementsCard() {
  return (
    <Card>
      <CardHeader
        title="Recent Announcements"
        action={<MegaphoneIcon className="h-5 w-5 text-slate-300" />} />
      
      <div className="mt-3 divide-y divide-slate-100 dark:divide-slate-800">
        {announcements.map((a) =>
        <div key={a.id} className="px-5 py-3.5">
            <div className="flex items-center gap-2 mb-1">
              <Badge tone={tagTone[a.tag]}>{a.tag}</Badge>
              <span className="text-xs text-slate-400">{a.date}</span>
            </div>
            <p className="font-semibold text-sm text-slate-800 dark:text-slate-100">
              {a.title}
            </p>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
              {a.body}
            </p>
          </div>
        )}
      </div>
    </Card>);

}
export function UpcomingEventsCard() {
  return (
    <Card>
      <CardHeader title="Upcoming Events" subtitle="Next 10 days" />
      <div className="mt-3 px-3 pb-3 space-y-1">
        {events.map((e) => {
          const s = eventStyle[e.type];
          return (
            <div
              key={e.id}
              className="flex items-center gap-3 rounded-2xl px-2 py-2 hover:bg-slate-50 dark:hover:bg-slate-800/60">
              
              <span
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl ${eventToneClass[s.tone]}`}>
                
                {s.icon}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">
                  {e.title}
                </p>
                <p className="text-xs text-slate-400">
                  {e.date} · {e.time}
                </p>
              </div>
              <Badge tone={s.tone === 'rose' ? 'rose' : 'slate'}>
                {e.type}
              </Badge>
            </div>);

        })}
      </div>
    </Card>);

}
export function ActivityFeed() {
  return (
    <Card>
      <CardHeader title="Recent Activity" />
      <div className="mt-3 px-5 pb-5 space-y-4">
        {activities.map((a, i) =>
        <div key={a.id} className="flex gap-3">
            <div className="flex flex-col items-center">
              <Avatar src={a.avatar} name={a.who} size={32} />
              {i < activities.length - 1 &&
            <span className="w-px flex-1 bg-slate-100 dark:bg-slate-800 mt-1" />
            }
            </div>
            <div className="pb-1">
              <p className="text-sm text-slate-600 dark:text-slate-300">
                <span className="font-semibold text-slate-800 dark:text-slate-100">
                  {a.who}
                </span>{' '}
                {a.action}{' '}
                <span className="font-semibold text-brand-600 dark:text-brand-300">
                  {a.target}
                </span>
              </p>
              <p className="text-xs text-slate-400 mt-0.5">{a.time}</p>
            </div>
          </div>
        )}
      </div>
    </Card>);

}
export function MiniCalendar() {
  const today = 14;
  const days = Array.from(
    {
      length: 31
    },
    (_, i) => i + 1
  );
  const eventDays = [15, 16, 17, 19, 22, 24];
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display font-bold text-slate-800 dark:text-slate-100">
          July 2026
        </h3>
        <MedalIcon className="h-5 w-5 text-slate-300" />
      </div>
      <div className="grid grid-cols-7 gap-1 text-center text-[11px] font-semibold text-slate-400 mb-1">
        {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((d, i) =>
        <span key={i}>{d}</span>
        )}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {Array.from({
          length: 2
        }).map((_, i) =>
        <span key={`e${i}`} />
        )}
        {days.map((d) => {
          const isToday = d === today;
          const hasEvent = eventDays.includes(d);
          return (
            <div
              key={d}
              className={`relative flex h-9 items-center justify-center rounded-xl text-sm font-medium ${isToday ? 'bg-brand-600 text-white font-bold' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'}`}>
              
              {d}
              {hasEvent && !isToday &&
              <span className="absolute bottom-1 h-1 w-1 rounded-full bg-warm-500" />
              }
            </div>);

        })}
      </div>
    </Card>);

}