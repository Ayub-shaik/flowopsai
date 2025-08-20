import React from "react";
import { useParams } from "react-router-dom";
import RunView from "../components/RunView";

export default function RunDetail() {
  // Support both /runs/:runId and /runs/:id
  const params = useParams();
  const runId = params.runId || params.id;

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-white">Run {runId ?? "?"}</h1>
      <RunView runId={runId} />
    </div>
  );
}
