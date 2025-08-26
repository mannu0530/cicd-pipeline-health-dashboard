
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000"

export async function fetchOverview() {
  const r = await fetch(`${API_BASE}/api/metrics/overview`)
  return r.json()
}

export async function fetchBuilds(params={}) {
  const q = new URLSearchParams(params).toString()
  const r = await fetch(`${API_BASE}/api/builds?${q}`)
  return r.json()
}

export function wsConnect(onMessage) {
  const ws = new WebSocket((API_BASE.replace(/^http/,'ws')) + "/ws")
  ws.onmessage = (ev) => {
    try { onMessage(JSON.parse(ev.data)) } catch {}
  }
  return ws
}
