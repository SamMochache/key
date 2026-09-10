import React, { useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { login } from '../lib/api';

export function Login() {
  const { authStatus, refreshSession } = useApp();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (authStatus === 'authenticated') {
    const from = (location.state as { from?: string } | null)?.from || '/';
    return <Navigate to={from} replace />;
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await login(email.trim(), password);
      await refreshSession();
      navigate((location.state as { from?: string } | null)?.from || '/', { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in. Please check your credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center px-4 py-8 sm:px-6 lg:px-8">
      <div className="relative w-full max-w-5xl overflow-hidden rounded-[2rem] border border-slate-200/80 bg-white shadow-softlg dark:border-slate-800 dark:bg-slate-900 lg:grid lg:grid-cols-[0.9fr_1.1fr]">
        <div className="relative hidden overflow-hidden bg-slate-900 px-10 py-12 text-white lg:flex lg:flex-col lg:justify-between dark:bg-slate-950">
          <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-brand-600/20 blur-3xl" />
          <div className="absolute -bottom-28 -left-20 h-64 w-64 rounded-full bg-brand-500/10 blur-3xl" />

          <div className="relative">
            <div className="flex items-center gap-4">
              <img src="/key-logo.svg" alt="KEY" className="h-16 w-20 object-contain object-left" />
              <div>
                <p className="font-display text-xl font-extrabold tracking-tight">STEMFORGE</p>
                <p className="text-xs font-medium text-slate-400">Key Organization</p>
              </div>
            </div>

            <div className="mt-20 max-w-sm">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-brand-400">School operating system</p>
              <h2 className="mt-4 font-display text-4xl font-extrabold leading-tight tracking-tight">
                Everything your school needs, in one place.
              </h2>
              <p className="mt-5 text-sm leading-7 text-slate-300">
                Manage learning, assessment, evidence, communication and student progress through one calm, connected experience.
              </p>
            </div>
          </div>

          <div className="relative flex flex-wrap gap-2 pt-10">
            {['Academics', 'Assessment', 'Student progress'].map((item) => (
              <span key={item} className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-slate-300">
                {item}
              </span>
            ))}
          </div>
        </div>

        <div className="flex items-center px-6 py-10 sm:px-10 sm:py-12 lg:px-14">
          <div className="w-full max-w-md mx-auto">
            <div className="mb-8 flex justify-center lg:justify-start">
              <img src="/key-logo.svg" alt="KEY" className="h-16 w-20 object-contain object-left" />
            </div>

            <div className="mb-8">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-600 dark:text-brand-400">Welcome back</p>
              <h1 className="mt-2 font-display text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">Sign in to KEY</h1>
              <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">Use your institution account to continue to your workspace.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-300">Email</span>
                <input
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@school.org"
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3.5 text-sm text-slate-900 outline-none transition-shadow placeholder:text-slate-400 focus:border-brand-400 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:placeholder:text-slate-600"
                />
              </label>

              <label className="block">
                <div className="mb-2 flex items-center justify-between">
                  <span className="block text-sm font-semibold text-slate-700 dark:text-slate-300">Password</span>
                </div>
                <input
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter your password"
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3.5 text-sm text-slate-900 outline-none transition-shadow placeholder:text-slate-400 focus:border-brand-400 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:placeholder:text-slate-600"
                />
              </label>

              {error && (
                <div role="alert" className="flex items-start gap-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700 dark:border-rose-500/20 dark:bg-rose-500/10 dark:text-rose-300">
                  <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-rose-100 text-xs font-bold dark:bg-rose-500/20">!</span>
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-2xl bg-brand-600 px-4 py-3.5 text-sm font-bold text-white shadow-lg shadow-brand-600/15 transition-all hover:-translate-y-0.5 hover:opacity-95 hover:shadow-xl disabled:translate-y-0 disabled:opacity-60 disabled:shadow-none"
              >
                {submitting ? 'Signing in…' : 'Sign in'}
              </button>
            </form>

            <div className="mt-8 flex items-center justify-center gap-2 text-xs text-slate-400 dark:text-slate-500">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              <span>Secure institution access</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
