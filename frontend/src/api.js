
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function fetchOverview() {
  try {
    const response = await fetch(`${API_BASE}/api/metrics/overview`)
    if (!response.ok) throw new Error('Failed to fetch overview')
    return await response.json()
  } catch (error) {
    console.error('Error fetching overview:', error)
    return null
  }
}

export async function fetchBuilds(filters = {}) {
  try {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value)
    })
    
    const response = await fetch(`${API_BASE}/api/builds?${params}`)
    if (!response.ok) throw new Error('Failed to fetch builds')
    return await response.json()
  } catch (error) {
    console.error('Error fetching builds:', error)
    return []
  }
}

export async function fetchChartData(days = 7) {
  try {
    const response = await fetch(`${API_BASE}/api/metrics/chart-data?days=${days}`)
    if (!response.ok) throw new Error('Failed to fetch chart data')
    return await response.json()
  } catch (error) {
    console.error('Error fetching chart data:', error)
    return []
  }
}

export async function fetchBuildTrends(days = 14) {
  try {
    const response = await fetch(`${API_BASE}/api/metrics/build-trends?days=${days}`)
    if (!response.ok) throw new Error('Failed to fetch build trends')
    return await response.json()
  } catch (error) {
    console.error('Error fetching build trends:', error)
    return []
  }
}

export async function fetchPipelinePerformance(limit = 10) {
  try {
    const response = await fetch(`${API_BASE}/api/metrics/pipeline-performance?limit=${limit}`)
    if (!response.ok) throw new Error('Failed to fetch pipeline performance')
    return await response.json()
  } catch (error) {
    console.error('Error fetching pipeline performance:', error)
    return []
  }
}

export function wsConnect(onMessage) {
  const ws = new WebSocket(`ws://${API_BASE.replace('http://', '').replace('https://', '')}/ws`)
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch (error) {
      console.error('WebSocket message parse error:', error)
    }
  }
  ws.onerror = (error) => console.error('WebSocket error:', error)
  ws.onclose = () => console.log('WebSocket connection closed')
  return ws
}
