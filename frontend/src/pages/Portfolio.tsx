import React from 'react';
import {
  UploadIcon,
  ImageIcon,
  FileTextIcon,
  VideoIcon,
  AwardIcon } from
'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { PORTFOLIO_IMG } from '../lib/data';
const items = [
{
  type: 'Artwork',
  title: 'Autumn Leaf Collage',
  date: 'Jul 12',
  img: PORTFOLIO_IMG,
  icon: ImageIcon,
  tone: 'warm' as const
},
{
  type: 'Certificate',
  title: 'Kind Helper Award',
  date: 'Jul 09',
  icon: AwardIcon,
  tone: 'brand' as const
},
{
  type: 'Project',
  title: 'World Continents Map',
  date: 'Jul 05',
  img: PORTFOLIO_IMG,
  icon: FileTextIcon,
  tone: 'emerald' as const
},
{
  type: 'Video',
  title: 'First Story Read Aloud',
  date: 'Jul 01',
  icon: VideoIcon,
  tone: 'brand' as const
},
{
  type: 'Artwork',
  title: 'Clay Bird Sculpture',
  date: 'Jun 28',
  img: PORTFOLIO_IMG,
  icon: ImageIcon,
  tone: 'warm' as const
},
{
  type: 'Observation',
  title: 'Pink Tower Mastery',
  date: 'Jun 24',
  icon: FileTextIcon,
  tone: 'emerald' as const
}];

export function Portfolio() {
  return (
    <div>
      <PageHeader
        title="Learning Portfolio"
        description="A living collection of each child’s creations, milestones, and moments of growth."
        actions={
        <Button>
            <UploadIcon className="h-4 w-4" /> Add to portfolio
          </Button>
        } />
      

      <div className="columns-1 sm:columns-2 lg:columns-3 gap-6 [column-fill:_balance]">
        {items.map((it, i) =>
        <Card
          key={i}
          className="mb-6 overflow-hidden break-inside-avoid hover:-translate-y-0.5 transition-transform">
          
            {it.img &&
          <img
            src={it.img}
            alt={it.title}
            className="w-full h-44 object-cover" />

          }
            <div className="p-4">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500">
                  <it.icon className="h-4 w-4" />
                </span>
                <Badge tone={it.tone}>{it.type}</Badge>
              </div>
              <p className="font-semibold text-slate-800 dark:text-slate-100">
                {it.title}
              </p>
              <p className="text-xs text-slate-400 mt-0.5">
                Added {it.date} · by Sophie Laurent
              </p>
            </div>
          </Card>
        )}
      </div>
    </div>);

}