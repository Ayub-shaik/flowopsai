import React, { useEffect, useState } from "react";
import { apiGet } from "../api";

export default function Models() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const API = import.meta.env.VITE_API_URL || "/api";

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data = await apiGet("/models");
        if (mounted) setModels(data);
      } catch (e) {
        console.error(e);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  if (loading) return <div className="p-4">Loading…</div>;

  if (!models.length) {
    return (
      <div className="p-4">
        <div className="text-white/70">No models yet. Start a run in Chat and the trainer will register a model when complete.</div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-white mb-4">Models</h1>
      <div className="overflow-auto">
        <table className="w-full text-left">
          <thead className="text-white/60">
            <tr>
              <th className="py-2 pr-4">ID</th>
              <th className="py-2 pr-4">Name</th>
              <th className="py-2 pr-4">Created</th>
              <th className="py-2 pr-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {models.map((m) => (
              <tr key={m.id} className="border-t border-white/10">
                <td className="py-2 pr-4">{m.id}</td>
                <td className="py-2 pr-4">{m.name}</td>
                <td className="py-2 pr-4">{new Date(m.created_at).toLocaleString()}</td>
                <td className="py-2 pr-4">
                  <a className="btn" href={`${API}/models/${m.id}/download`} target="_blank" rel="noreferrer">
                    Download
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
