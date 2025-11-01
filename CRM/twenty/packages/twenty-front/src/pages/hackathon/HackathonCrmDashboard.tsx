import { useEffect, useMemo, useState, type CSSProperties } from 'react';
import type { Contact } from '@/hackathon/api/types';
import { CRM_API_BASE_URL } from '@/hackathon/api/constants';
import { PageContainer } from '@/ui/layout/page/components/PageContainer';

const card: CSSProperties = { border: '1px solid #e5e7eb', borderRadius: 8, padding: 20, marginBottom: 24 };
const row: CSSProperties = { borderBottom: '1px solid #e5e7eb' };
const cell: CSSProperties = { padding: '12px 8px', verticalAlign: 'top' };

const formatSince = (iso?: string | null) => {
  if (!iso) return 'No interactions yet';
  const ms = Date.now() - new Date(iso).getTime();
  const mins = Math.max(1, Math.floor(ms / 60000));
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
};

export const HackathonCrmDashboard = () => {
  const [search, setSearch] = useState('');
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>();

  const query = useMemo(() => {
    const q = new URLSearchParams();
    if (search.trim()) q.set('search', search.trim());
    return q.toString();
  }, [search]);

  const load = async (signal?: AbortSignal) => {
    setIsLoading(true);
    setError(undefined);
    try {
      const res = await fetch(`${CRM_API_BASE_URL}/contacts${query ? `?${query}` : ''}`, { signal });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as { items: Contact[]; total: number };
      setContacts(data.items);
      setTotal(data.total);
    } catch (e) {
      if ((e as Error).name !== 'AbortError') {
        setError('Unable to load CRM data.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    void load(controller.signal);
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]);

  return (
    <PageContainer>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24, gap: 12 }}>
        <div>
          <h1 style={{ margin: 0 }}>CRM</h1>
          <p style={{ margin: 0, opacity: 0.7 }}>Simple list of contacts.</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            placeholder="Search name, title, or company"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ padding: 10, border: '1px solid #e5e7eb', borderRadius: 6, minWidth: 280 }}
          />
          <button
            onClick={() => load()}
            disabled={isLoading}
            style={{ padding: '10px 12px', border: '1px solid #e5e7eb', borderRadius: 6, background: '#fff' }}
            aria-label="Refresh CRM data"
          >
            {isLoading ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div style={{ border: '1px solid #fecaca', background: '#fee2e2', color: '#991b1b', borderRadius: 6, padding: 12, marginBottom: 16 }}>
          {error}
        </div>
      )}

      <div style={card}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
          <div style={{ opacity: 0.7, fontSize: 12 }}>Total</div>
          <div style={{ fontSize: 18, fontWeight: 600 }}>{total}</div>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={row}>
              <th style={{ ...cell, textAlign: 'left', color: '#6b7280', fontSize: 12 }}>Name & Title</th>
              <th style={{ ...cell, textAlign: 'left', color: '#6b7280', fontSize: 12 }}>Company</th>
              <th style={{ ...cell, textAlign: 'left', color: '#6b7280', fontSize: 12 }}>Stage</th>
              <th style={{ ...cell, textAlign: 'left', color: '#6b7280', fontSize: 12 }}>Tags</th>
              <th style={{ ...cell, textAlign: 'left', color: '#6b7280', fontSize: 12 }}>Last interaction</th>
            </tr>
          </thead>
          <tbody>
            {contacts.length === 0 ? (
              <tr><td style={cell} colSpan={5}><div style={{ textAlign: 'center', opacity: 0.7 }}>No contacts yet.</div></td></tr>
            ) : (
              contacts.map((c) => (
                <tr key={c.id} style={row}>
                  <td style={cell}><strong>{c.name}</strong><br/><span style={{ opacity: 0.8 }}>{c.title ?? '—'}</span></td>
                  <td style={cell}>{c.company ?? '—'}</td>
                  <td style={cell}>{c.relationship_stage}</td>
                  <td style={cell}>
                    {c.tags?.length ? (
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {c.tags.map((t) => <span key={t} style={{ border: '1px solid #e5e7eb', borderRadius: 999, padding: '2px 8px', fontSize: 12 }}>{t}</span>)}
                      </div>
                    ) : '—'}
                  </td>
                  <td style={cell}>{formatSince(c.last_interaction_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </PageContainer>
  );
};
