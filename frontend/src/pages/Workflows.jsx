import React, { useEffect, useState } from "react";
import { apiGet } from "../api.js";

export default function Workflows() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    // try backend; if it fails, keep client list (so UI still works)
    apiGet("/workflows").then(setItems).catch(() => {});
  }, []);

  function addWorkflow() {
    const id = "w" + (items.length + 1);
    const wf = { id, name: `Workflow ${items.length + 1}`, description: "Ingest → Train → Evaluate" };
    setItems((x) => [wf, ...x]); // client-side add so you SEE it immediately
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xl font-semibold">Workflows</h2>
        <button className="btn" onClick={addWorkflow}>New Workflow</button>
      </div>
      <div className="grid md:grid-cols-2 gap-3">
        {items.map((w) => (
          <div key={w.id} className="p-3 rounded-xl border border-white/10 bg-white/5">
            <div className="font-semibold">{w.name}</div>
            <div className="text-white/60 text-sm">{w.description}</div>
          </div>
        ))}
        {!items.length && <div className="text-white/50">No workflows yet.</div>}
      </div>
    </div>
  );
}
