import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import RunView from "../components/RunView";
import StatusBadge from "../components/StatusBadge";
import { apiGet } from "../api";

export default function RunDetail() {
  const params = useParams();
  const runId = params.runId || params.id;

  const [run, setRun] = useState(null);
  const [loading, setLoading] = useState(true);

  // initial fetch
  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const data = await apiGet(`/runs/${runId}`);
        if (mounted) setRun(data);
      } catch (e) {
        console.error(e);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    if (runId) load();
    return () => {
      mounted = false;
    };
  }, [runId]);

  // live poll every 2s for status + metrics
  useEffect(() => {
    if (!runId) return;
    let cancelled = false;
    const timer = setInterval(async () => {
      try {
        const data = await apiGet(`/runs/${runId}`);
        if (!cancelled) setRun(data);
      } catch (e) {
        // non-fatal; keep polling
        console.debug("poll error", e);
      }
    }, 2000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [runId]);

  return (
    <div className="p-4 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white">Run {runId ?? "?"}</h1>
        {run && <StatusBadge status={run.status} />}
      </div>

      <div className="card">
        <div className="badge mb-3">Live timeline</div>
        <RunView runId={runId} />
      </div>

      <div className="card">
        <div className="badge mb-3">Metrics</div>
        {loading && <div className="text-white/60">Loading…</div>}
        {!loading && !run?.metrics && (
          <div className="text-white/60">No metrics yet.</div>
        )}
        {!loading && run?.metrics && (
          <pre className="text-white/80 text-sm overflow-auto">
{JSON.stringify(run.metrics, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
