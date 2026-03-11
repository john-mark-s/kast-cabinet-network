import { useState, useEffect } from 'react';
import type { Changelog } from '../types/graph';

const BASE_PATH = import.meta.env.BASE_URL;

interface UseChangelogResult {
  changelog: Changelog | null;
  loading: boolean;
  error: string | null;
  totalEvents: number;
}

let cachedChangelog: Changelog | null = null;

export function useChangelog(): UseChangelogResult {
  const [changelog, setChangelog] = useState<Changelog | null>(cachedChangelog);
  const [loading, setLoading] = useState(!cachedChangelog);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (cachedChangelog) {
      setChangelog(cachedChangelog);
      setLoading(false);
      return;
    }

    const url = `${BASE_PATH}data/changelog.json`;
    fetch(url)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return res.json() as Promise<Changelog>;
      })
      .then(data => {
        cachedChangelog = data;
        setChangelog(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load changelog.json:', err);
        setError(err.message || 'Failed to load changelog');
        setLoading(false);
      });
  }, []);

  const totalEvents = changelog?.weeks.reduce(
    (sum, week) => sum + week.events.length, 0
  ) ?? 0;

  return { changelog, loading, error, totalEvents };
}
