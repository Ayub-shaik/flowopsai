// frontend/src/pages/Insights.jsx
import React, { useEffect, useState } from "react";
import { apiGet } from "../api";

export default function Insights() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiGet("/insights");
        if (!cancelled) setData(res);
      } catch (e) {
        if (!cancelled) setErr(e.message || "Failed to load insights");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return <div className="p-4"><div className="text-white/70">Loading insights…</div></div>;
  }
  if (err) {
    return <div className="p-4"><div className="text-red-400">Error: {err}</div></div>;
  }
  if (!data) {
    return <div className="p-4"><div className="text-white/70">No insights yet.</div></div>;
  }

  const t = data.totals || {};
  const latest = data.latest_runs || [];

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-xl font-bold">Insights</h1>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        <StatCard label="Total runs" value={t.runs ?? 0} />
        <StatCard label="Models" value={t.models ?? 0} />
        <StatCard label="Queued" value={t.queued ?? 0} />
        <StatCard label="Running" value={t.running ?? 0} />
        <StatCard label="Completed" value={t.completed ?? 0} />
      </div>

      {/* Latest runs table */}
      <div className="card">
        <div className="badge mb-3">Latest runs</div>
        {latest.length === 0 ? (
          <div className="text-white/60">No recent runs.</div>
        ) : (
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead className="text-white/60">
                <tr>
                  <th className="text-left p-2">ID</th>
                  <th className="text-left p-2">Status</th>
                  <th className="text-left p-2">Created</th>
                  <th className="text-left p-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {latest.map((r) => (
                  <tr key={r.id} className="border-t border-white/10">
                    <td className="p-2">{r.id}</td>
                    <td className="p-2">
                      <span className="px-2 py-0.5 rounded bg-white/10">
                        {r.status}
                      </span>
                    </td>
                    <td className="p-2">{new Date(r.created_at).toLocaleString()}</td>
                    <td className="p-2">
                      <a href={`/runs/${r.id}`} className="underline">Open</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="card flex flex-col items-start">
      <div className="text-white/60 text-sm">{label}</div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  );
}
