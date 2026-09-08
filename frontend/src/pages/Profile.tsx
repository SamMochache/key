import React, { useEffect, useState } from 'react';
import { Loader2Icon, SaveIcon, UserIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Avatar } from '../components/ui/Avatar';
import { getMyProfile, updateMyProfile, type SelfProfile } from '../lib/profileApi';

export function Profile() {
  const [profile, setProfile] = useState<SelfProfile | null>(null);
  const [form, setForm] = useState({ first_name: '', last_name: '', phone_number: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    getMyProfile().then((data) => {
      setProfile(data);
      setForm({ first_name: data.first_name, last_name: data.last_name, phone_number: data.phone_number || '' });
    }).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load your profile.')).finally(() => setLoading(false));
  }, []);

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true); setMessage(''); setError('');
    try {
      const data = await updateMyProfile(form);
      setProfile(data);
      setForm({ first_name: data.first_name, last_name: data.last_name, phone_number: data.phone_number || '' });
      setMessage('Profile updated successfully.');
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to save your profile.'); }
    finally { setSaving(false); }
  };

  if (loading) return <Card className="p-10 flex justify-center"><Loader2Icon className="h-7 w-7 animate-spin text-brand-600" /></Card>;
  if (!profile) return <Card className="p-6"><p className="text-sm text-rose-600">{error || 'Your profile could not be loaded.'}</p></Card>;

  return <div>
    <PageHeader title="My Profile" description="View and update the personal information connected to your account." />
    {error && <Card className="mb-5 p-4 border-rose-200 dark:border-rose-900"><p className="text-sm text-rose-600 dark:text-rose-400">{error}</p></Card>}
    {message && <Card className="mb-5 p-4 border-emerald-200 dark:border-emerald-900"><p className="text-sm text-emerald-600 dark:text-emerald-400">{message}</p></Card>}
    <div className="grid lg:grid-cols-[280px_1fr] gap-5">
      <Card className="p-6 text-center">
        <Avatar src={profile.profile_photo || undefined} name={profile.full_name} size={96} className="mx-auto" />
        <h2 className="mt-4 font-display font-extrabold text-xl text-slate-800 dark:text-slate-100">{profile.full_name}</h2>
        <p className="text-sm text-slate-400 mt-1">{profile.role}</p>
        <div className="mt-5 text-left space-y-3 text-sm"><p><span className="text-slate-400">Email</span><br /><span className="font-semibold text-slate-700 dark:text-slate-200 break-all">{profile.email}</span></p><p><span className="text-slate-400">Account status</span><br /><span className="font-semibold text-slate-700 dark:text-slate-200">{profile.status}</span></p></div>
      </Card>
      <Card className="p-6">
        <div className="flex items-center gap-3 mb-6"><span className="h-10 w-10 rounded-2xl bg-brand-50 dark:bg-slate-800 flex items-center justify-center text-brand-600"><UserIcon className="h-5 w-5" /></span><div><h2 className="font-display font-bold text-lg">Personal information</h2><p className="text-sm text-slate-400">Only your own account information can be changed here.</p></div></div>
        <form onSubmit={save} className="grid sm:grid-cols-2 gap-5">
          <Field label="First name" value={form.first_name} onChange={(value) => setForm({ ...form, first_name: value })} required />
          <Field label="Last name" value={form.last_name} onChange={(value) => setForm({ ...form, last_name: value })} required />
          <Field label="Email" value={profile.email} disabled />
          <Field label="Phone number" value={form.phone_number} onChange={(value) => setForm({ ...form, phone_number: value })} />
          <div className="sm:col-span-2 flex justify-end"><Button type="submit" disabled={saving}>{saving ? <Loader2Icon className="h-4 w-4 animate-spin" /> : <SaveIcon className="h-4 w-4" />}{saving ? 'Saving…' : 'Save changes'}</Button></div>
        </form>
      </Card>
    </div>
  </div>;
}

function Field({ label, value, onChange, disabled, required }: { label: string; value: string; onChange?: (value: string) => void; disabled?: boolean; required?: boolean }) {
  return <label className="block"><span className="block text-sm font-semibold text-slate-600 dark:text-slate-300 mb-2">{label}</span><input value={value} onChange={(event) => onChange?.(event.target.value)} disabled={disabled} required={required} className="w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-brand-200 dark:focus:ring-brand-900 disabled:bg-slate-50 disabled:text-slate-400 dark:disabled:bg-slate-800/60" /></label>;
}
