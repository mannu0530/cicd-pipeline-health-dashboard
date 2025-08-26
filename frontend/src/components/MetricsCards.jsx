
import React from 'react'

export default function MetricsCards({ overview }){
  return (
    <div className="cards">
      <div className="card">
        <div className="label">Success Rate</div>
        <div className="value">{overview?.success_rate ?? 0}%</div>
      </div>
      <div className="card">
        <div className="label">Failure Rate</div>
        <div className="value">{overview?.failure_rate ?? 0}%</div>
      </div>
      <div className="card">
        <div className="label">Avg Build Time</div>
        <div className="value">{overview?.avg_build_time_seconds ? Math.round(overview.avg_build_time_seconds) + 's' : '—'}</div>
      </div>
      <div className="card">
        <div className="label">Last Build</div>
        <div className="value">{overview?.last_build_status ?? '—'}</div>
      </div>
    </div>
  )
}
