import React, { useEffect, useState } from 'react';
import { GlobeIcon, KeyRoundIcon, Loader2Icon, SaveIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useApp } from '../context/AppContext';
import { changeMyPassword, getMyProfile, updateMyProfile } from '../lib/profileApi';

export function Settings() {
  const { dark, toggleDark, refreshSession } = useApp();
  const [language, setLanguage] = useState('en');
  const [timezone, setTimezone] = useState('Africa/Nairobi');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [password, setPassword] = useState({ current_password: '', new_password: '', confirm_password: '' });

  useEffect(() => {
    let cancelled = false;
    getMyProfile().then((data) => {
      if (cancelled) return;
      setLanguage(data.preferred_language || 'en');
      setTimezone(data.timezone || 'Africa/Nairobi');
    }).catch((err) => { if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load settings.'); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  const savePreferences = async (event: React.FormEvent) => {
    event.preventDefault(); setSaving(true); setMessage(''); setError('');
    try {
      await updateMyProfile({ preferred_language: language, timezone });
      await refreshSession();
      setMessage('Preferences saved successfully.');
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to save preferences.'); }
    finally { setSaving(false); }
  };

  const savePassword = async (event: React.FormEvent) => {
    event.preventDefault(); setPasswordSaving(true); setMessage(''); setError('');
    try {
      await changeMyPassword(password);
      setPassword({ current_password: '', new_password: '', confirm_password: '' });
      setMessage('Password changed successfully.');
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to change your password.'); }
    finally { setPasswordSaving(false); }
  };

  if (loading) return <Card className="p-10 flex justify-center"><Loader2Icon className="h-7 w-7 animate-spin text-brand-600" /></Card>;
  return <div className="max-w-4xl">
    <PageHeader title="Settings" description="Manage your account preferences and security." />
    {error && <Card className="mb-5 p-4 border-rose-200 dark:border-rose-900"><p className="text-sm text-rose-600 dark:text-rose-400">{error}</p></Card>}
    {message && <Card className="mb-5 p-4 border-emerald-200 dark:border-emerald-900"><p className="text-sm text-emerald-600 dark:text-emerald-400">{message}</p></Card>}
    <div className="space-y-5">
      <Card className="p-6"><div className="flex items-center gap-3 mb-5"><GlobeIcon className="h-5 w-5 text-brand-600" /><div><h2 className="font-display font-bold">Preferences</h2><p className="text-sm text-slate-400">These settings belong to your account.</p></div></div><form onSubmit={savePreferences} className="grid sm:grid-cols-2 gap-5"><Select label="Language" value={language} onChange={setLanguage} options={[['en', 'English']]} /><Select label="Timezone" value={timezone} onChange={setTimezone} options={[["Africa/Nairobi", "Africa/Nairobi"], ["UTC", "UTC"]]} /><div className="sm:col-span-2 flex justify-end"><Button type="submit" disabled={saving}>{saving ? <Loader2Icon className="h-4 w-4 animate-spin" /> : <SaveIcon className="h-4 w-4" />}{saving ? 'Saving…' : 'Save preferences'}</Button></div></form></Card>
      <Card className="p-6"><div className="flex items-center gap-3 mb-5"><span className="h-10 w-10 rounded-2xl bg-brand-50 dark:bg-slate-800 flex items-center justify-center text-brand-600"><KeyRoundIcon className="h-5 w-5" /></span><div><h2 className="font-display font-bold">Password</h2><p className="text-sm text-slate-400">Change the password for your signed-in account.</p></div></div><form onSubmit={savePassword} className="grid sm:grid-cols-2 gap-5"><Password label="Current password" value={password.current_password} onChange={(value) => setPassword({ ...password, current_password: value })} /><Password label="New password" value={password.new_password} onChange={(value) => setPassword({ ...password, new_password: value })} /><Password label="Confirm new password" value={password.confirm_password} onChange={(value) => setPassword({ ...password, confirm_password: value })} /><div className="sm:col-span-2 flex justify-end"><Button type="submit" disabled={passwordSaving}>{passwordSaving ? <Loader2Icon className="h-4 w-4 animate-spin" /> : <KeyRoundIcon className="h-4 w-4" />}{passwordSaving ? 'Changing…' : 'Change password'}</Button></div></form></Card>
      <Card className="p-6 flex items-center justify-between gap-4"><div><h2 className="font-display font-bold">Appearance</h2><p className="text-sm text-slate-400">Choose the display mode for this device.</p></div><Button variant="secondary" onClick={toggleDark}>{dark ? 'Use light mode' : 'Use dark mode'}</Button></Card>
    </div>
  </div>;
}

function Select({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: string[][] }) { return <label><span className="block text-sm font-semibold text-slate-600 dark:text-slate-300 mb-2">{label}</span><select value={value} onChange={(event) => onChange(event.target.value)} className="w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-brand-200">{options.map(([key, text]) => <option key={key} value={key}>{text}</option>)}</select></label>; }
function Password({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) { return <label><span className="block text-sm font-semibold text-slate-600 dark:text-slate-300 mb-2">{label}</span><input type="password" value={value} onChange={(event) => onChange(event.target.value)} required className="w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-brand-200" /></label>; }
