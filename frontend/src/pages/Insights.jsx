import React, { useEffect, useState } from "react";
import { apiGet } from "../api.js";

export default function Insights() {
  const [metrics, setMetrics] = useState(null);
  useEffect(() => {
    apiGet("/insights")
      .then(setMetrics)
      .catch(() => setMetrics({ runs_total: 0, success_rate: 0 }));
  }, []);
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-3">Insights</h2>
      <pre className="text-white/80 whitespace-pre-wrap">{JSON.stringify(metrics, null, 2)}</pre>
    </div>
  );
}
