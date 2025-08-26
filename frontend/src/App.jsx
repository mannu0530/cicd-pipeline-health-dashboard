
import React, { useEffect, useState, useRef } from 'react'
import { fetchOverview, fetchBuilds, wsConnect } from './api'
import MetricsCards from './components/MetricsCards.jsx'
import BuildsTable from './components/BuildsTable.jsx'
import { SuccessFailureChart, AvgBuildTimeChart } from './components/Charts.jsx'
import LogViewer from './components/LogViewer.jsx'

export default function App(){
  const [overview, setOverview] = useState(null)
  const [builds, setBuilds] = useState([])
  const [filters, setFilters] = useState({ provider:'', status:'', q:'' })
  const [chartData, setChartData] = useState({sf:[], avg:[]})
  const [selectedBuild, setSelectedBuild] = useState(null)
  const wsRef = useRef(null)
  const [dark, setDark] = useState(true)

  async function load(){
    setOverview(await fetchOverview())
    setBuilds(await fetchBuilds(clean(filters)))
    // For demo chart data, create simple aggregates from builds
    const rows = await fetchBuilds({limit:100})
    const times = rows.slice(0,20).reverse().map((r,i)=>({time:`#${r.id}`, success: r.status==='success'?1:0, failed: r.status==='failed'?1:0, avg: r.duration_seconds||0}))
    setChartData({sf: times.map(t=>({time:t.time, success: t.success, failed: t.failed})), avg: times.map(t=>({time:t.time, avg:t.avg}))})
  }

  useEffect(() => { load() }, [])
  useEffect(() => { load() }, [filters.provider, filters.status])

  useEffect(() => {
    wsRef.current = wsConnect((evt) => {
      if (evt.type?.includes('build_')) { load() }
    })
    return () => { try { wsRef.current?.close() } catch {} }
  }, [])

  const wsConnected = wsRef.current && wsRef.current.readyState === 1

  return (
    <div className={dark ? 'app dark' : 'app'}>
      <div className="header">
        <h2>CI/CD Pipeline Health Dashboard</h2>
        <div style={{display:'flex',gap:12,alignItems:'center'}}>
          <div className="ws">{wsConnected ? 'Live updates ✓' : 'Connecting...'}</div>
          <button onClick={()=>setDark(!dark)}>{dark ? 'Light' : 'Dark'}</button>
        </div>
      </div>

      <MetricsCards overview={overview} />

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12, marginTop:12}}>
        <SuccessFailureChart data={chartData.sf} />
        <AvgBuildTimeChart data={chartData.avg} />
      </div>

      <div className="filters" style={{marginTop:12}}>
        <select value={filters.provider} onChange={e => setFilters({...filters, provider:e.target.value})}>
          <option value="">All Providers</option>
          <option value="github">GitHub</option>
          <option value="gitlab">GitLab</option>
          <option value="jenkins">Jenkins</option>
        </select>
        <select value={filters.status} onChange={e => setFilters({...filters, status:e.target.value})}>
          <option value="">All Statuses</option>
          <option value="success">Success</option>
          <option value="failed">Failed</option>
          <option value="running">Running</option>
        </select>
        <input placeholder="Search pipeline" value={filters.q} onChange={e => setFilters({...filters, q:e.target.value})} />
        <button onClick={load}>Refresh</button>
      </div>

      <BuildsTable builds={builds.map(b=>({...b, onClick: ()=>setSelectedBuild(b)}))} />

      {selectedBuild && (
        <div style={{marginTop:12}}>
          <div className="card" style={{padding:12}}>
            <div style={{display:'flex', justifyContent:'space-between'}}>
              <div>
                <div className="label">Selected Build</div>
                <div className="value">{selectedBuild.pipeline} — {selectedBuild.status}</div>
              </div>
              <div>
                <button onClick={()=>setSelectedBuild(null)}>Close</button>
              </div>
            </div>
            <LogViewer provider={selectedBuild.provider} externalId={selectedBuild.external_id || selectedBuild.id} />
          </div>
        </div>
      )}
    </div>
  )
}

function clean(obj){
  const out = {}
  for (const [k,v] of Object.entries(obj)){
    if (v) out[k]=v
  }
  return out
}
