import React from "react";
import { useParams } from "react-router-dom";

export default function RunDetail() {
  const { id } = useParams();
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-2">Run #{id}</h2>
      <div className="text-white/70">Live events streaming will appear here once the backend WS is wired.</div>
    </div>
  );
}
