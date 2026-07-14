import React from 'react';
import { Link } from 'react-router-dom';
import {
  StarIcon,
  TargetIcon,
  BookOpenIcon,
  TrophyIcon,
  SparklesIcon,
  CheckCircle2Icon } from
'lucide-react';
import { PageHeader } from '../ui/PageHeader';
import { Card, CardHeader } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { PORTFOLIO_IMG } from '../../lib/data';
const homework = [
{
  title: 'Finish leaf drawing',
  subject: 'Culture',
  done: true
},
{
  title: 'Read 2 pages aloud',
  subject: 'Language',
  done: true
},
{
  title: 'Golden bead addition',
  subject: 'Maths',
  done: false
}];

const goals = [
{
  label: 'Read a whole story by myself',
  progress: 80
},
{
  label: 'Help a friend each day',
  progress: 60
},
{
  label: 'Finish the world map work',
  progress: 45
}];

const achievements = [
{
  icon: TrophyIcon,
  label: 'Kind Helper',
  tone: 'bg-warm-500'
},
{
  icon: StarIcon,
  label: 'Reading Star',
  tone: 'bg-brand-600'
},
{
  icon: SparklesIcon,
  label: 'Great Focus',
  tone: 'bg-emerald-500'
}];

export function StudentDashboard({ name }: {name: string;}) {
  return (
    <div>
      <PageHeader
        title={`Hi ${name.split(' ')[0]}! 🌱`}
        description="Here’s your learning garden today. Every little step helps you grow!" />
      

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-6 bg-brand-600 border-brand-600 text-white">
            <p className="text-brand-100 font-semibold">Today’s adventure</p>
            <h2 className="font-display text-2xl font-extrabold mt-1">
              Story Sequencing & Leaf Study
            </h2>
            <p className="text-brand-100 mt-2">
              You have 3 fun activities waiting. You’ve already finished 2!
            </p>
            <div className="mt-4 h-2 w-full rounded-full bg-white/20 overflow-hidden">
              <div
                className="h-full rounded-full bg-white"
                style={{
                  width: '66%'
                }} />
              
            </div>
          </Card>

          <Card>
            <CardHeader title="My Homework" subtitle="What to do today" />
            <div className="px-3 pb-3 mt-2 space-y-1">
              {homework.map((h) =>
              <div
                key={h.title}
                className="flex items-center gap-3 rounded-2xl px-3 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/60">
                
                  <CheckCircle2Icon
                  className={`h-6 w-6 ${h.done ? 'text-emerald-500' : 'text-slate-300 dark:text-slate-600'}`} />
                
                  <div className="flex-1">
                    <p
                    className={`font-semibold text-sm ${h.done ? 'text-slate-400 line-through' : 'text-slate-800 dark:text-slate-100'}`}>
                    
                      {h.title}
                    </p>
                    <p className="text-xs text-slate-400">{h.subject}</p>
                  </div>
                  {!h.done && <Badge tone="warm">To do</Badge>}
                </div>
              )}
            </div>
          </Card>

          <Card>
            <CardHeader
              title="My Goals"
              action={<TargetIcon className="h-5 w-5 text-slate-300" />} />
            
            <div className="px-5 pb-5 mt-2 space-y-4">
              {goals.map((g) =>
              <div key={g.label}>
                  <div className="flex justify-between text-sm mb-1.5">
                    <span className="font-semibold text-slate-700 dark:text-slate-200">
                      {g.label}
                    </span>
                    <span className="text-slate-400">{g.progress}%</span>
                  </div>
                  <div className="h-2.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                    <div
                    className="h-full rounded-full bg-emerald-500"
                    style={{
                      width: `${g.progress}%`
                    }} />
                  
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="p-5">
            <h3 className="font-display font-bold text-slate-800 dark:text-slate-100 mb-4">
              My Achievements
            </h3>
            <div className="grid grid-cols-3 gap-3">
              {achievements.map((a) =>
              <div
                key={a.label}
                className="flex flex-col items-center text-center gap-2">
                
                  <span
                  className={`flex h-14 w-14 items-center justify-center rounded-3xl text-white ${a.tone}`}>
                  
                    <a.icon className="h-6 w-6" />
                  </span>
                  <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">
                    {a.label}
                  </span>
                </div>
              )}
            </div>
          </Card>

          <Card className="overflow-hidden">
            <CardHeader
              title="My Portfolio"
              action={
              <Link
                to="/portfolio"
                className="text-sm font-bold text-brand-600">
                
                  See all
                </Link>
              } />
            
            <div className="p-4 pt-3">
              <img
                src={PORTFOLIO_IMG}
                alt="My artwork"
                className="w-full h-40 object-cover rounded-2xl" />
              
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100 mt-3">
                My Autumn Leaves
              </p>
            </div>
          </Card>

          <Card className="p-5">
            <div className="flex items-center gap-2 mb-2">
              <BookOpenIcon className="h-5 w-5 text-brand-600" />
              <h3 className="font-display font-bold text-slate-800 dark:text-slate-100">
                Teacher Feedback
              </h3>
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              “Wonderful focus today, Mia! I loved how carefully you sorted your
              leaves. ⭐”
            </p>
          </Card>
        </div>
      </div>
    </div>);

}