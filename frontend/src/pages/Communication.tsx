import React, { useEffect, useMemo, useState } from 'react';
import { InboxIcon, MailIcon, PlusIcon, SearchIcon, SendIcon } from 'lucide-react';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { EmptyState } from '../components/ui/EmptyState';
import { Avatar } from '../components/ui/Avatar';
import { listContacts, listMessages, markMessageRead, sendMessage, type CommunicationContact, type CommunicationMessage } from '../lib/communicationApi';
import { cn } from '../lib/utils';

export function Communication() {
  const [folder, setFolder] = useState<'inbox' | 'sent'>('inbox');
  const [messages, setMessages] = useState<CommunicationMessage[]>([]);
  const [contacts, setContacts] = useState<CommunicationContact[]>([]);
  const [active, setActive] = useState<CommunicationMessage | null>(null);
  const [search, setSearch] = useState('');
  const [composeOpen, setComposeOpen] = useState(false);
  const [recipientSearch, setRecipientSearch] = useState('');
  const [recipient, setRecipient] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const loadMessages = () => {
    setLoading(true);
    setError('');
    listMessages(folder).then((data) => { setMessages(data); setActive((current) => current && data.some((item) => item.id === current.id) ? data.find((item) => item.id === current.id) || null : data[0] || null); }).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load messages.')).finally(() => setLoading(false));
  };

  useEffect(() => { loadMessages(); }, [folder]);
  useEffect(() => { if (!composeOpen) return; listContacts(recipientSearch).then(setContacts).catch((err) => setError(err instanceof Error ? err.message : 'Unable to load contacts.')); }, [composeOpen, recipientSearch]);

  const filtered = useMemo(() => {
    const value = search.trim().toLowerCase();
    if (!value) return messages;
    return messages.filter((message) => `${message.subject} ${message.body} ${message.sender_name} ${message.recipient_name}`.toLowerCase().includes(value));
  }, [messages, search]);

  const openMessage = async (message: CommunicationMessage) => {
    setActive(message);
    if (folder === 'inbox' && !message.is_read) {
      try {
        const updated = await markMessageRead(message.id);
        setMessages((current) => current.map((item) => item.id === updated.id ? updated : item));
        setActive(updated);
      } catch (err) { setError(err instanceof Error ? err.message : 'Unable to mark message as read.'); }
    }
  };

  const submit = async () => {
    if (!recipient || !subject.trim() || !body.trim()) return;
    setSaving(true); setError('');
    try {
      await sendMessage({ recipient, subject: subject.trim(), body: body.trim() });
      setComposeOpen(false); setRecipient(''); setSubject(''); setBody(''); setRecipientSearch('');
      setFolder('sent');
      await listMessages('sent').then(setMessages);
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to send message.'); } finally { setSaving(false); }
  };

  return <div>
    <PageHeader title="Communication" description="Private, institution-scoped messages between the people who make the school community work." actions={<Button onClick={() => setComposeOpen(true)}><PlusIcon className="h-4 w-4" /> New message</Button>} />
    {error && <Card className="mb-5 p-4"><p className="text-sm text-rose-600 dark:text-rose-400">{error}</p></Card>}
    <Card className="overflow-hidden">
      <div className="flex flex-col lg:flex-row min-h-[620px]">
        <aside className="lg:w-72 border-b lg:border-b-0 lg:border-r border-slate-100 dark:border-slate-800 flex flex-col">
          <div className="p-4 space-y-3">
            <div className="flex gap-2"><Button variant={folder === 'inbox' ? 'primary' : 'secondary'} onClick={() => setFolder('inbox')}><InboxIcon className="h-4 w-4" /> Inbox</Button><Button variant={folder === 'sent' ? 'primary' : 'secondary'} onClick={() => setFolder('sent')}><SendIcon className="h-4 w-4" /> Sent</Button></div>
            <div className="flex items-center gap-2 rounded-2xl bg-slate-100 dark:bg-slate-800 px-3 py-2"><SearchIcon className="h-4 w-4 text-slate-400" /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search messages" className="flex-1 bg-transparent text-sm outline-none" /></div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {loading ? <p className="p-5 text-sm text-slate-400">Loading messages…</p> : filtered.length === 0 ? <div className="p-5"><EmptyState icon="Mail" title="No messages" description={folder === 'inbox' ? 'Your inbox is clear.' : 'Messages you send will appear here.'} /></div> : filtered.map((message) => <button key={message.id} onClick={() => openMessage(message)} className={cn('w-full text-left px-4 py-3 border-b border-slate-50 dark:border-slate-800/80 hover:bg-slate-50 dark:hover:bg-slate-800/60', active?.id === message.id && 'bg-brand-50 dark:bg-slate-800')}><div className="flex items-start gap-3"><Avatar name={folder === 'inbox' ? message.sender_name : message.recipient_name} size={38} /><div className="min-w-0 flex-1"><div className="flex items-center justify-between gap-2"><p className={cn('text-sm truncate', !message.is_read && folder === 'inbox' ? 'font-extrabold text-slate-900 dark:text-white' : 'font-semibold text-slate-700 dark:text-slate-200')}>{folder === 'inbox' ? message.sender_name : message.recipient_name}</p><span className="text-[10px] text-slate-400">{new Date(message.sent_at).toLocaleDateString()}</span></div><p className="text-xs font-semibold text-slate-600 dark:text-slate-300 truncate mt-0.5">{message.subject}</p><p className="text-xs text-slate-400 truncate mt-0.5">{message.body}</p></div>{!message.is_read && folder === 'inbox' && <span className="mt-2 h-2 w-2 rounded-full bg-brand-600" />}</div></button>)}
          </div>
        </aside>
        <section className="flex-1 flex flex-col">
          {!active ? <div className="flex-1 flex items-center justify-center p-8"><EmptyState icon="Mail" title="Select a message" description="Choose a conversation from your inbox or sent messages." /></div> : <><header className="px-6 py-5 border-b border-slate-100 dark:border-slate-800"><div className="flex items-start gap-3"><Avatar name={folder === 'inbox' ? active.sender_name : active.recipient_name} size={44} /><div className="min-w-0"><p className="font-bold text-slate-900 dark:text-white">{folder === 'inbox' ? active.sender_name : active.recipient_name}</p><p className="text-xs text-slate-400">{folder === 'inbox' ? active.sender_email : active.recipient_email}</p><div className="mt-2"><Badge tone="slate">{new Date(active.sent_at).toLocaleString()}</Badge></div></div></div></header><article className="flex-1 overflow-y-auto p-6"><h2 className="font-display text-xl font-extrabold text-slate-900 dark:text-white">{active.subject}</h2><div className="mt-6 whitespace-pre-wrap text-sm leading-7 text-slate-700 dark:text-slate-300">{active.body}</div></article></>}
        </section>
      </div>
    </Card>

    {composeOpen && <div className="fixed inset-0 z-50 bg-slate-950/40 flex items-center justify-center p-4"><Card className="w-full max-w-2xl p-6"><div className="flex items-center justify-between mb-5"><div><h2 className="font-display text-xl font-extrabold text-slate-900 dark:text-white">New message</h2><p className="text-sm text-slate-400 mt-1">Messages stay inside your institution.</p></div><button onClick={() => setComposeOpen(false)} className="text-slate-400 text-xl">×</button></div><div className="space-y-4"><label className="block text-sm font-semibold text-slate-600 dark:text-slate-300">Recipient<input value={recipientSearch} onChange={(e) => { setRecipientSearch(e.target.value); setRecipient(''); }} placeholder="Search by name or email" className="mt-1 w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3 text-sm" />{recipientSearch && !recipient && <div className="mt-1 max-h-40 overflow-y-auto rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">{contacts.map((contact) => <button type="button" key={contact.id} onClick={() => { setRecipient(contact.id); setRecipientSearch(contact.name); }} className="block w-full px-3 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-800"><span className="block text-sm font-semibold">{contact.name}</span><span className="block text-xs text-slate-400">{contact.email}</span></button>)}</div>}</label><Field label="Subject" value={subject} onChange={setSubject} /><label className="block text-sm font-semibold text-slate-600 dark:text-slate-300">Message<textarea rows={7} value={body} onChange={(e) => setBody(e.target.value)} className="mt-1 w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3 text-sm" /></label><div className="flex justify-end gap-2"><Button variant="secondary" onClick={() => setComposeOpen(false)}>Cancel</Button><Button onClick={submit} disabled={saving || !recipient || !subject.trim() || !body.trim()}><SendIcon className="h-4 w-4" /> {saving ? 'Sending…' : 'Send message'}</Button></div></div></Card></div>}
  </div>;
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) { return <label className="block text-sm font-semibold text-slate-600 dark:text-slate-300">{label}<input value={value} onChange={(e) => onChange(e.target.value)} className="mt-1 w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3 text-sm" /></label>; }
