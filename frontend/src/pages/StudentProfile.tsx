import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import type { MouseEvent } from 'react';
import { StudentProfile as LegacyStudentProfile } from './StudentProfileLegacy';

const TAB_NAMES = new Set([
  'Overview', 'Enrollment', 'Attendance', 'Assessments', 'Assignments',
  'Behaviour', 'Portfolio', 'Teacher Notes', 'AI Reports',
]);

const tabSlug = (label: string) => label.toLowerCase().replace(/\s+/g, '-');

export function StudentProfile() {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const tab = new URLSearchParams(location.search).get('tab');
    if (!tab) return;

    const expected = [...TAB_NAMES].find((name) => tabSlug(name) === tab);
    if (!expected) return;

    let attempts = 0;
    const interval = window.setInterval(() => {
      const button = [...document.querySelectorAll('button')]
        .find((element) => element.textContent?.trim() === expected) as HTMLButtonElement | undefined;
      if (button) {
        button.click();
        window.clearInterval(interval);
      } else if (++attempts >= 40) {
        window.clearInterval(interval);
      }
    }, 50);

    return () => window.clearInterval(interval);
  }, [location.search]);

  const handleTabClick = (event: MouseEvent<HTMLDivElement>) => {
    const target = event.target as HTMLElement | null;
    const button = target?.closest('button');
    const label = button?.textContent?.trim() || '';
    if (!TAB_NAMES.has(label)) return;

    const params = new URLSearchParams(location.search);
    if (label === 'Overview') params.delete('tab');
    else params.set('tab', tabSlug(label));
    navigate({ pathname: location.pathname, search: params.toString() ? `?${params.toString()}` : '' }, { replace: true });
  };

  return (
    <div onClickCapture={handleTabClick}>
      <LegacyStudentProfile />
    </div>
  );
}
