
import React from 'react'

export default function BuildsTable({ builds }){
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Provider</th>
          <th>Pipeline</th>
          <th>Status</th>
          <th>Duration</th>
          <th>Started</th>
          <th>Link</th>
        </tr>
      </thead>
      <tbody>
        {builds.map(b => (
          <tr key={b.id} onClick={() => b.onClick && b.onClick()} style={{cursor: b.onClick ? 'pointer' : 'default'}}>
            <td>{b.provider}</td>
            <td>{b.pipeline}</td>
            <td><span className={`status ${b.status}`}>{b.status}</span></td>
            <td>{b.duration_seconds ? b.duration_seconds + 's' : '—'}</td>
            <td>{b.started_at ? new Date(b.started_at).toLocaleString() : '—'}</td>
            <td>{b.web_url ? <a className="link" href={b.web_url} target="_blank">Open</a> : '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
