const API = import.meta.env.VITE_API_URL || "/api";

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

// --- WS for run events ---
export function connectRunEvents(runId, onEvent) {
  // same host, nginx proxies /ws -> backend
  const wsProto = location.protocol === "https:" ? "wss" : "ws";
  const wsUrl = `${wsProto}://${location.host}/ws/runs/${runId}`;
  const ws = new WebSocket(wsUrl);
  ws.onmessage = (msg) => {
    try { onEvent(JSON.parse(msg.data)); } catch {}
  };
  return ws;
}
