
import React from 'react'

export default function MetricsCards({ overview }){
  // Calculate counts from percentages if available
  const totalBuilds = overview?.total_builds || 0
  const successCount = Math.round((overview?.success_rate || 0) * totalBuilds / 100)
  const failureCount = Math.round((overview?.failure_rate || 0) * totalBuilds / 100)
  
  // Format average build time
  const formatBuildTime = (seconds) => {
    if (!seconds) return '—'
    if (seconds < 60) return `${Math.round(seconds)}s`
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`
    return `${Math.round(seconds / 3600)}h ${Math.round((seconds % 3600) / 60)}m`
  }

  return (
    <div className="cards">
      <div className="card">
        <div className="label">Success Rate</div>
        <div className="value success">{overview?.success_rate ?? 0}%</div>
        <div className="sub-value">{successCount} builds</div>
      </div>
      <div className="card">
        <div className="label">Failure Rate</div>
        <div className="value failure">{overview?.failure_rate ?? 0}%</div>
        <div className="sub-value">{failureCount} builds</div>
      </div>
      <div className="card">
        <div className="label">Avg Build Time</div>
        <div className="value">{formatBuildTime(overview?.avg_build_time_seconds)}</div>
        <div className="sub-value">per build</div>
      </div>
      <div className="card">
        <div className="label">Last Build</div>
        <div className="value">{overview?.last_build_status ?? '—'}</div>
        <div className="sub-value">{overview?.last_build_at ? new Date(overview.last_build_at).toLocaleTimeString() : '—'}</div>
      </div>
    </div>
  )
}
