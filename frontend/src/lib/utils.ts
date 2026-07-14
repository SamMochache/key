import { twMerge } from 'tailwind-merge';

export function cn(...classes: (string | false | null | undefined)[]) {
  return twMerge(classes.filter(Boolean).join(' '));
}

export function initials(name: string) {
  return name.
  split(' ').
  map((n) => n[0]).
  slice(0, 2).
  join('').
  toUpperCase();
}