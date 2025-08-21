import React, { useEffect, useState } from "react";
import { apiGet } from "../api";

export default function Automations() {
  const [flags, setFlags] = useState(null);

  useEffect(() => {
    apiGet("/features").then(setFlags).catch(() => setFlags({}));
  }, []);

  const n8nEnabled = !!flags?.n8n;
  const mcpEnabled = !!flags?.mcp;
  const n8nUrl = "/n8n/";

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-xl font-bold">Automations</h1>

      <div className="card">
        <div className="badge mb-3">DIY Workbench (n8n)</div>
        <p className="text-white/70 mb-3">Drag‑and‑drop workflow builder. When enabled, we embed n8n below.</p>

        <div className="flex items-center gap-3 mb-4">
          <span className="text-white/70">n8n enabled</span>
          <span className={`px-2 py-1 rounded ${n8nEnabled ? "bg-green-600/40" : "bg-white/10"}`}>
            {n8nEnabled ? "ON" : "OFF"}
          </span>
          {n8nEnabled && (
            <>
              <a className="btn" href={n8nUrl} target="_blank" rel="noreferrer">Open n8n</a>
              <a
                className="btn"
                href="/automations/n8n"
                onClick={(e) => {
                  e.preventDefault();
                  document.getElementById("n8n-frame")?.scrollIntoView({ behavior: "smooth", block: "start" });
                }}
              >
                Preview below
              </a>
            </>
          )}
        </div>

        {!n8nEnabled && (
          <div className="text-white/60">
            Not enabled. Set <code>ENABLE_N8N=1</code> (frontend .env), add the <code>n8n</code> service in
            <code> docker-compose.yaml</code>, and restart.
          </div>
        )}
      </div>

      {n8nEnabled && (
        <div className="card">
          <div className="badge mb-3">Embedded n8n (experimental)</div>
          <div id="n8n-frame" className="h-[70vh] border border-white/10 rounded-xl overflow-hidden">
            <iframe title="n8n" src={n8nUrl} style={{ width: "100%", height: "100%", border: 0 }}
                    allow="clipboard-read; clipboard-write" />
          </div>
        </div>
      )}

      <div className="card">
        <div className="badge mb-3">Chat Orchestrator (MCP)</div>
        <p className="text-white/80">
          Natural‑language orchestration of tools and workflows. This area will wire MCP so agents can call tools securely.
          For now it’s a placeholder.
        </p>
        <div className="flex items-center gap-3 mt-3">
          <span className="text-white/70">MCP enabled</span>
          <span className={`px-2 py-1 rounded ${mcpEnabled ? "bg-green-600/40" : "bg-white/10"}`}>
            {mcpEnabled ? "ON" : "OFF"}
          </span>
        </div>
      </div>
    </div>
  );
}
