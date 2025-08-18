import React, { useEffect, useState } from "react";
import { apiGet } from "../api.js";

export default function Models() {
  const [models, setModels] = useState([]);
  useEffect(() => {
    apiGet("/models")
      .then(setModels)
      .catch(() => setModels([{ id: "m1", name: "gpt-4o-mini", provider: "openai" }]));
  }, []);
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-3">Models</h2>
      <div className="grid md:grid-cols-2 gap-3">
        {models.map((m) => (
          <div key={m.id} className="p-3 rounded-xl border border-white/10 bg-white/5">
            <div className="font-semibold">{m.name}</div>
            <div className="text-white/60 text-sm">Provider: {m.provider}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
