// frontend/src/pages/RunDetail.jsx
import React from "react";
import { useParams } from "react-router-dom";
import RunView from "../components/RunView";

export default function RunDetail() {
  const { runId } = useParams();
  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-white">Run {runId}</h1>
      <div className="card mt-4">
        <div className="badge mb-3">Live timeline</div>
        <RunView runId={runId} />
      </div>
    </div>
  );
}
