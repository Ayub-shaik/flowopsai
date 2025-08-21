import { useEffect, useState } from "react";
import { connectRunEvents } from "../api";
import AgentTimeline from "./AgentTimeline";

export default function RunView({ runId }) {
  const [events, setEvents] = useState([]);
  useEffect(() => {
    if (!runId) return;
    const ws = connectRunEvents(runId, (ev) =>
      setEvents((prev) => [...prev, ev])
    );
    return () => ws.close();
  }, [runId]);
  return <AgentTimeline events={events} />;
}
