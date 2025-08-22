import React, { useState } from "react";
import { apiPost } from "../api";
import { useNavigate } from "react-router-dom";

export default function AppGen() {
  const [name, setName] = useState("My App");
  const [template, setTemplate] = useState("react-lite");
  const [spec, setSpec] = useState("// describe your app here");
  const [busy, setBusy] = useState(false);
  const [last, setLast] = useState(null);
  const navigate = useNavigate();

  async function onGenerate(e) {
    e?.preventDefault?.();
    setBusy(true);
    setLast(null);
    try {
      // 1) Generate (your existing generator endpoint)
      // Expecting response to include: app_id (optional), preview_url, zip_url
      const gen = await apiPost("/appgen/generate", {
        name,
        template,
        prompt: spec,
        spec
      });

      const appName = gen.name || name;
      const preview_url = gen.preview_url || (gen.app_id ? `/api/apps/${gen.app_id}` : null);
      const zip_url = gen.zip_url || null;

      setLast({ preview_url, zip_url });

      // 2) Register in DB (new endpoint)
      try {
        await apiPost("/apps", {
          name: appName,
          template,
          preview_url,
          zip_url,
          meta: { raw: gen }, // stash full generator response for later
          status: "ready"
        });
      } catch (_) {
        // non-fatal – UI still shows immediate links
      }

    } catch (err) {
      alert(`Generation failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-xl font-bold">App Generator</h1>

      <form onSubmit={onGenerate} className="card space-y-3">
        <div className="grid md:grid-cols-3 gap-3">
          <div className="md:col-span-1">
            <label className="text-sm text-white/70">Name</label>
            <input className="input" value={name} onChange={e=>setName(e.target.value)} />
          </div>
          <div className="md:col-span-1">
            <label className="text-sm text-white/70">Template</label>
            <select className="input" value={template} onChange={e=>setTemplate(e.target.value)}>
              <option value="react-lite">React (lite)</option>
              <option value="vanilla">Vanilla</option>
              <option value="streamlit">Streamlit</option>
            </select>
          </div>
        </div>

        <div>
          <label className="text-sm text-white/70">Specification</label>
          <textarea className="input" rows={8} value={spec} onChange={e=>setSpec(e.target.value)} />
        </div>

        <div className="flex gap-2">
          <button className="btn" disabled={busy}>{busy ? "Generating…" : "Generate"}</button>
          <button
            type="button"
            className="btn"
            onClick={() => navigate("/apps")}
          >
            My Apps
          </button>
        </div>
      </form>

      {last && (
        <div className="card">
          <div className="badge mb-3">Result</div>
          <div className="flex gap-2">
            {last.preview_url && (
              <a className="btn" href={last.preview_url} target="_blank" rel="noreferrer">Open Preview</a>
            )}
            {last.zip_url && (
              <a className="btn" href={last.zip_url}>Download ZIP</a>
            )}
            <button className="btn" onClick={() => navigate("/apps")}>Go to “My Apps”</button>
          </div>
        </div>
      )}
    </div>
  );
}
