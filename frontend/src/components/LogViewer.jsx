
import React, { useEffect, useState } from 'react'

export default function LogViewer({ provider, externalId }){
  const [logs, setLogs] = useState(null)
  useEffect(() => {
    let mounted = true
    if (!provider || !externalId) return
    fetch(`${import.meta.env.VITE_API_BASE || 'http://localhost:8000'}/api/logs/${provider}/${externalId}`)
      .then(r => r.json())
      .then(d => { if (mounted) setLogs(d.logs) })
    return () => { mounted = false }
  }, [provider, externalId])

  return (
    <div className="card" style={{marginTop:12}}>
      <div className="label">Logs</div>
      <div className="value" style={{fontSize:13, marginTop:8}}>
        <div style={{height:240, overflowY:'auto', background:'#07080b', color:'#cbd5e1', padding:12, borderRadius:8, fontFamily:'ui-monospace, monospace'}}>
          {logs ? (typeof logs === 'string' ? logs.split('\n').map((l,i)=>(<div key={i}>{l}</div>)) : JSON.stringify(logs)) : 'Loading logs...'}
        </div>
      </div>
    </div>
  )
}
