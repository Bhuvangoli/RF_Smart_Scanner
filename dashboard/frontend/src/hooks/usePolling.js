import { useEffect, useRef, useState } from "react";

/**
 * Polls `fetcher` on an interval and exposes the latest result.
 * Used to update the frontend "without requiring a full page
 * refresh" (Dashboard_PRD.md section 5.4).
 */
export function usePolling(fetcher, intervalMs = 1000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const savedFetcher = useRef(fetcher);
  savedFetcher.current = fetcher;

  useEffect(() => {
    let cancelled = false;
    let timer;

    async function tick() {
      try {
        const result = await savedFetcher.current();
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err);
      } finally {
        if (!cancelled) timer = setTimeout(tick, intervalMs);
      }
    }

    tick();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [intervalMs]);

  return { data, error };
}
