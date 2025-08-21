import React from "react";

export default function StatusBadge({ status }) {
  const color =
    status === "running" ? "bg-yellow-500/20 text-yellow-300" :
    status === "completed" ? "bg-green-500/20 text-green-300" :
    status === "failed" ? "bg-red-500/20 text-red-300" :
    "bg-white/10 text-white/70";
  return (
    <span className={`px-2 py-1 rounded-md text-sm ${color}`}>
      {status}
    </span>
  );
}
