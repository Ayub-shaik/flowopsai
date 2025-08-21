import React, { useEffect, useRef } from "react";
import { clsx } from "clsx";

export default function AgentTimeline({ events = [] }) {
  const listRef = useRef(null);

  // auto-scroll to last event whenever events update
  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [events]);

  if (!events.length) {
    return (
      <div className="text-white/50">
        No events yet — agents will appear here as they work.
      </div>
    );
  }

  return (
    <div ref={listRef} className="max-h-[55vh] overflow-auto pr-2">
      <ol className="relative border-l border-white/10 pl-6">
        {events.map((e, i) => (
          <li key={i} className="mb-4">
            <span
              className={clsx(
                "absolute -left-2 top-1 w-3 h-3 rounded-full",
                e.level === "error"
                  ? "bg-red-400"
                  : e.level === "warn"
                  ? "bg-yellow-300"
                  : "bg-green-400"
              )}
            />
            <div className="text-sm text-white/60">
              {new Date(e.ts).toLocaleTimeString()}
            </div>
            <div className="font-semibold">{e.title}</div>
            {e.detail && <div className="text-white/70">{e.detail}</div>}
          </li>
        ))}
      </ol>
    </div>
  );
}
