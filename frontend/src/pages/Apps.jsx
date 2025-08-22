import React, { useEffect, useState } from "react";
import { apiGet, apiDelete } from "../api";

export default function Apps() {
  const [apps, setApps] = useState(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      const data = await apiGet("/apps");
      setApps(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function onDelete(id) {
    if (!confirm("Delete this app? This will remove its DB entry (and files if configured).")) return;
    await apiDelete(`/apps/${id}`);
    await load();
  }

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-xl font-bold">My Apps</h1>
      <div className="card">
        {loading && <div className="text-white/60">Loading…</div>}
        {!loading && (!apps || apps.length === 0) && (
          <div className="text-white/60">No apps yet. Generate one from AppGen.</div>
        )}
        {!loading && apps && apps.length > 0 && (
          <div className="space-y-3">
            {apps.map(a => (
              <div key={a.id} className="flex items-center justify-between bg-white/5 p-3 rounded-xl">
                <div>
                  <div className="font-semibold">#{a.id} · {a.name}</div>
                  <div className="text-white/60 text-sm">
                    {a.template || "custom"} · {new Date(a.created_at).toLocaleString()}
                  </div>
                </div>
                <div className="flex gap-2">
                  {a.preview_url && (
                    <a className="btn" href={a.preview_url} target="_blank" rel="noreferrer">Preview</a>
                  )}
                  {a.zip_url && (
                    <a className="btn" href={a.zip_url}>Download ZIP</a>
                  )}
                  <button className="btn" onClick={() => onDelete(a.id)}>Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
