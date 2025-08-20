const API = import.meta.env.VITE_API_URL || "/api";

// If you set VITE_WS_URL, we’ll use that. Otherwise we derive from the page origin.
const WS_BASE =
  (import.meta.env.VITE_WS_URL && import.meta.env.VITE_WS_URL.replace(/^http/, "ws")) ||
  (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host;

export async function apiGet(path) {
  const r = await fetch(`${API}${path}`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function apiPost(path, body) {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// 🔥 WebSocket connector for run events
export function connectRunEvents(runId, onEvent) {
  const url = `${WS_BASE}/ws/runs/${runId}`;
  const ws = new WebSocket(url);

  ws.onopen = () => console.log("WS connected:", url);
  ws.onmessage = (evt) => {
    try {
      const data = JSON.parse(evt.data);
      onEvent?.(data);
    } catch (e) {
      console.error("WS parse error", e);
    }
  };
  ws.onerror = (e) => console.error("WS error", e);
  ws.onclose = () => console.log("WS closed:", url);

  return ws;
}
