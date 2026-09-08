import React, { useEffect, useState } from 'react';
import { SaveIcon, UserIcon, MailIcon, PhoneIcon, GraduationCapIcon, Loader2Icon } from 'lucide-react';
import { Card, CardHeader } from '../components/ui/Card';
import { Avatar } from '../components/ui/Avatar';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { useApp } from '../context/AppContext';
import { getCurrentUser, updateCurrentUser, type CurrentUser } from '../lib/api';

export function MyProfile() {
  const { user, role, refreshSession } = useApp();
  const [profile, setProfile] = useState<CurrentUser | null>(user);
  const [form, setForm] = useState({ first_name: user?.first_name || '', last_name: user?.last_name || '', phone_number: user?.phone_number || '', preferred_language: user?.preferred_language || '', timezone: user?.timezone || '' });
  const [loading, setLoading] = useState(!user);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    getCurrentUser().then(data => {
      if (cancelled) return;
      setProfile(data);
      setForm({ first_name: data.first_name || '', last_name: data.last_name || '', phone_number: data.phone_number || '', preferred_language: data.preferred_language || '', timezone: data.timezone || '' });
    }).catch(err => { if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load your profile.'); }).finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true); setMessage(''); setError('');
    try {
      const updated = await updateCurrentUser(form);
      setProfile(updated);
      setForm({ first_name: updated.first_name || '', last_name: updated.last_name || '', phone_number: updated.phone_number || '', preferred_language: updated.preferred_language || '', timezone: updated.timezone || '' });
      await refreshSession();
      setMessage('Profile updated successfully.');
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to save your profile.'); }
    finally { setSaving(false); }
  };

  if (loading) return <Card className="p-10 text-center text-sm text-slate-500">Loading your profile…</Card>;
  if (!profile) return <Card className="p-8 text-center text-sm text-rose-600">{error || 'Your profile could not be loaded.'}</Card>;

  const input = 'w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-3 text-sm text-slate-800 dark:text-slate-100 outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10';
  return <div className="max-w-4xl mx-auto space-y-6">
    <div><p className="text-sm font-semibold text-brand-600">Account</p><h1 className="font-display text-3xl font-extrabold text-slate-900 dark:text-white mt-1">My Profile</h1><p className="text-sm text-slate-500 mt-1">Manage the personal information connected to your KEY account.</p></div>
    <Card className="p-6"><div className="flex flex-col sm:flex-row items-start sm:items-center gap-5"><Avatar src={profile.profile_photo || undefined} name={profile.full_name} size={80} ring /><div className="flex-1"><div className="flex items-center gap-2 flex-wrap"><h2 className="text-xl font-bold text-slate-900 dark:text-white">{profile.full_name}</h2><Badge tone="emerald">{role}</Badge></div><p className="text-sm text-slate-400 mt-1">{profile.email}</p><p className="text-xs text-slate-400 mt-2">Account status: {profile.status}</p></div></div></Card>
    <Card><CardHeader title="Personal information" subtitle="Changes apply only to your authenticated account." />
      <form onSubmit={save} className="px-5 pb-6 space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <label><span className="block text-xs font-semibold text-slate-500 mb-1.5">First name</span><div className="relative"><UserIcon className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" /><input className={input + ' pl-10'} value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} required /></div></label>
          <label><span className="block text-xs font-semibold text-slate-500 mb-1.5">Last name</span><input className={input} value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} required /></label>
          <label><span className="block text-xs font-semibold text-slate-500 mb-1.5">Email</span><div className="relative"><MailIcon className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" /><input className={input + ' pl-10 bg-slate-50 dark:bg-slate-800'} value={profile.email} disabled /></div><span className="block text-[11px] text-slate-400 mt-1">Email is managed by your school account.</span></label>
          <label><span className="block text-xs font-semibold text-slate-500 mb-1.5">Phone number</span><div className="relative"><PhoneIcon className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" /><input className={input + ' pl-10'} value={form.phone_number} onChange={e => setForm({ ...form, phone_number: e.target.value })} /></div></label>
          <label><span className="block text-xs font-semibold text-slate-500 mb-1.5">Preferred language</span><select className={input} value={form.preferred_language} onChange={e => setForm({ ...form, preferred_language: e.target.value })}><option value="">Select language</option><option value="en">English</option><option value="sw">Swahili</option></select></label>
          <label><span className="block text-xs font-semibold text-slate-500 mb-1.5">Timezone</span><input className={input} value={form.timezone} onChange={e => setForm({ ...form, timezone: e.target.value })} placeholder="Africa/Nairobi" /></label>
        </div>
        {message && <p className="rounded-2xl bg-emerald-50 dark:bg-emerald-500/10 px-4 py-3 text-sm text-emerald-700 dark:text-emerald-400">{message}</p>}
        {error && <p className="rounded-2xl bg-rose-50 dark:bg-rose-500/10 px-4 py-3 text-sm text-rose-700 dark:text-rose-400">{error}</p>}
        <div className="flex justify-end"><Button type="submit" disabled={saving}>{saving ? <Loader2Icon className="h-4 w-4 animate-spin" /> : <SaveIcon className="h-4 w-4" />}{saving ? 'Saving…' : 'Save changes'}</Button></div>
      </form>
    </Card>
    <Card className="p-5"><div className="flex gap-3"><GraduationCapIcon className="h-5 w-5 text-brand-600 mt-0.5" /><div><p className="font-semibold text-slate-800 dark:text-slate-100">School account</p><p className="text-sm text-slate-500 mt-1">Your student admission, enrollment and academic records are controlled by your school. They cannot be changed from this page.</p></div></div></Card>
  </div>;
}
