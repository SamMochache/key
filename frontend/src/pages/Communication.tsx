import React, { useState } from 'react';
import { SendIcon, SearchIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Avatar } from '../components/ui/Avatar';
import { AnnouncementsCard } from '../components/widgets/Widgets';
import { PROFILES } from '../lib/data';
import { cn } from '../lib/utils';
const threads = [
{
  id: 't1',
  name: 'Sophie Laurent',
  role: 'Ocean Guide',
  last: 'Mia had a wonderful day!',
  time: '2m',
  unread: true
},
{
  id: 't2',
  name: 'Front Office',
  role: 'Administration',
  last: 'Your conference is confirmed.',
  time: '1h',
  unread: false
},
{
  id: 't3',
  name: 'Priya Nair',
  role: 'Meadow Guide',
  last: 'Thank you for the update.',
  time: '1d',
  unread: false
}];

const messages = [
{
  me: false,
  text: 'Good afternoon! Just wanted to share that Mia showed lovely focus during her leaf study today.',
  time: '2:14 PM'
},
{
  me: true,
  text: 'That’s wonderful to hear, thank you Sophie! She’s been talking about leaves all week 🍂',
  time: '2:20 PM'
},
{
  me: false,
  text: 'So lovely. I’ve added a photo of her collage to the portfolio for you to see.',
  time: '2:22 PM'
}];

export function Communication() {
  const [active, setActive] = useState('t1');
  const [draft, setDraft] = useState('');
  return (
    <div>
      <PageHeader
        title="Communication"
        description="Warm, direct conversations between families and guides — plus school-wide notices." />
      

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="overflow-hidden flex flex-col lg:flex-row h-[560px]">
            {/* Threads */}
            <div className="lg:w-64 border-b lg:border-b-0 lg:border-r border-slate-100 dark:border-slate-800 flex flex-col">
              <div className="p-3">
                <div className="flex items-center gap-2 rounded-2xl bg-slate-100 dark:bg-slate-800 px-3 py-2">
                  <SearchIcon className="h-4 w-4 text-slate-400" />
                  <input
                    placeholder="Search messages"
                    className="flex-1 bg-transparent text-sm outline-none" />
                  
                </div>
              </div>
              <div className="flex-1 overflow-y-auto">
                {threads.map((t) =>
                <button
                  key={t.id}
                  onClick={() => setActive(t.id)}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-3 text-left transition-colors',
                    active === t.id ?
                    'bg-brand-50 dark:bg-slate-800' :
                    'hover:bg-slate-50 dark:hover:bg-slate-800/60'
                  )}>
                  
                    <Avatar
                    name={t.name}
                    size={40}
                    src={PROFILES.teacher.avatar} />
                  
                    <div className="min-w-0 flex-1">
                      <div className="flex justify-between">
                        <p className="font-semibold text-sm text-slate-800 dark:text-slate-100 truncate">
                          {t.name}
                        </p>
                        <span className="text-[11px] text-slate-400">
                          {t.time}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 truncate">
                        {t.last}
                      </p>
                    </div>
                    {t.unread &&
                  <span className="h-2 w-2 rounded-full bg-brand-600" />
                  }
                  </button>
                )}
              </div>
            </div>

            {/* Conversation */}
            <div className="flex-1 flex flex-col">
              <div className="flex items-center gap-3 px-5 py-3.5 border-b border-slate-100 dark:border-slate-800">
                <Avatar
                  name="Sophie Laurent"
                  size={38}
                  src={PROFILES.teacher.avatar} />
                
                <div>
                  <p className="font-semibold text-sm text-slate-800 dark:text-slate-100">
                    Sophie Laurent
                  </p>
                  <p className="text-xs text-emerald-500 font-medium">
                    ● Online
                  </p>
                </div>
              </div>
              <div className="flex-1 overflow-y-auto p-5 space-y-4">
                {messages.map((m, i) =>
                <div
                  key={i}
                  className={cn(
                    'flex',
                    m.me ? 'justify-end' : 'justify-start'
                  )}>
                  
                    <div
                    className={cn(
                      'max-w-[75%] rounded-3xl px-4 py-2.5 text-sm',
                      m.me ?
                      'bg-brand-600 text-white rounded-br-md' :
                      'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-bl-md'
                    )}>
                    
                      <p>{m.text}</p>
                      <p
                      className={cn(
                        'text-[10px] mt-1',
                        m.me ? 'text-brand-100' : 'text-slate-400'
                      )}>
                      
                        {m.time}
                      </p>
                    </div>
                  </div>
                )}
              </div>
              <div className="p-3 border-t border-slate-100 dark:border-slate-800 flex items-center gap-2">
                <input
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  placeholder="Write a message…"
                  className="flex-1 rounded-2xl bg-slate-100 dark:bg-slate-800 px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-brand-500/40" />
                
                <button
                  onClick={() => setDraft('')}
                  className="flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-600 text-white hover:bg-brand-700">
                  
                  <SendIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </Card>
        </div>

        <AnnouncementsCard />
      </div>
    </div>);

}