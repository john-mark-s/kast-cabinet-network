import { useState, useEffect } from 'react';
import type { Graph } from '../types/graph';

const BASE_PATH = import.meta.env.BASE_URL;

interface UseGraphDataResult {
  graph: Graph | null;
  loading: boolean;
  error: string | null;
}

let cachedGraph: Graph | null = null;

export function useGraphData(): UseGraphDataResult {
  const [graph, setGraph] = useState<Graph | null>(cachedGraph);
  const [loading, setLoading] = useState(!cachedGraph);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (cachedGraph) {
      setGraph(cachedGraph);
      setLoading(false);
      return;
    }

    const url = `${BASE_PATH}data/graph.json`;
    fetch(url)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return res.json() as Promise<Graph>;
      })
      .then(data => {
        cachedGraph = data;
        setGraph(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load graph.json:', err);
        setError(err.message || 'Failed to load graph data');
        setLoading(false);
      });
  }, []);

  return { graph, loading, error };
}
