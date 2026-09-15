import { useCallback, useEffect, useState } from 'react';

function readCache(key) {
  try {
    const raw = sessionStorage.getItem(`vizreport:${key}`);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export default function useRemoteSnapshot(key, loader, fallback) {
  const cached = readCache(key);
  const [data, setData] = useState(cached?.data ?? fallback);
  const [state, setState] = useState(cached ? 'stale' : 'offline');
  const [updatedAt, setUpdatedAt] = useState(cached?.updatedAt ?? fallback?.updated_at ?? null);
  const [error, setError] = useState(null);
  const [attempt, setAttempt] = useState(0);

  const retry = useCallback(() => setAttempt((value) => value + 1), []);

  useEffect(() => {
    const nextCached = readCache(key);
    setData(nextCached?.data ?? fallback);
    setState(nextCached ? 'stale' : 'offline');
    setUpdatedAt(nextCached?.updatedAt ?? fallback?.updated_at ?? null);
    setError(null);
  }, [fallback, key]);

  useEffect(() => {
    let active = true;
    loader()
      .then((next) => {
        if (!active) return;
        const time = next.updated_at ?? new Date().toISOString();
        setData(next);
        setUpdatedAt(time);
        setState('live');
        setError(null);
        try { sessionStorage.setItem(`vizreport:${key}`, JSON.stringify({ data: next, updatedAt: time })); } catch { /* storage is best effort */ }
      })
      .catch((reason) => {
        if (!active) return;
        setError(reason);
        setState(readCache(key) ? 'stale' : 'offline');
      });
    return () => { active = false; };
  }, [attempt, key, loader]);

  return { data, state, updatedAt, error, retry };
}
