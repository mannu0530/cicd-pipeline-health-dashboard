
import React, { useEffect, useState, useRef } from 'react'
import { fetchOverview, fetchBuilds, wsConnect } from './api'
import MetricsCards from './components/MetricsCards.jsx'
import BuildsTable from './components/BuildsTable.jsx'
import { SuccessFailureChart, AvgBuildTimeChart, BuildTrendsChart, PipelinePerformanceChart } from './components/Charts.jsx'
import BuildStats from './components/BuildStats.jsx'
import LogViewer from './components/LogViewer.jsx'

export default function App(){
  const [overview, setOverview] = useState(null)
  const [builds, setBuilds] = useState([])
  const [filters, setFilters] = useState({ provider:'', status:'', q:'' })
  const [chartSettings, setChartSettings] = useState({
    days: 7,
    showTrends: true,
    showPipelinePerformance: true
  })
  const [selectedBuild, setSelectedBuild] = useState(null)
  const wsRef = useRef(null)
  const [dark, setDark] = useState(true)

  async function load(){
    setOverview(await fetchOverview())
    setBuilds(await fetchBuilds(clean(filters)))
  }

  useEffect(() => { 
    console.log('App mounted, loading data...')
    load() 
  }, [])
  
  useEffect(() => { 
    console.log('Filters changed, reloading data...')
    load() 
  }, [filters.provider, filters.status])

  useEffect(() => {
    wsRef.current = wsConnect((evt) => {
      if (evt.type?.includes('build_')) { load() }
    })
    return () => { try { wsRef.current?.close() } catch {} }
  }, [])

  const wsConnected = wsRef.current && wsRef.current.readyState === 1

  return (
    <div className={dark ? 'app' : 'app light'}>
      <div className="header">
        <h2>CI/CD Pipeline Health Dashboard</h2>
        <div style={{display:'flex',gap:12,alignItems:'center'}}>
          <div className="ws">{wsConnected ? 'Live updates ✓' : 'Connecting...'}</div>
          <button className="theme-toggle" onClick={()=>setDark(!dark)}>
            {dark ? '☀️ Light' : '🌙 Dark'}
          </button>
        </div>
      </div>

      <MetricsCards overview={overview} />

      {/* Build Statistics */}
      <div style={{marginTop: 12}}>
        <BuildStats />
      </div>

      {/* Chart Controls */}
      <div className="chart-controls" style={{marginTop: 12, marginBottom: 12}}>
        <div style={{display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap'}}>
          <label>
            Time Range:
            <select 
              value={chartSettings.days} 
              onChange={e => setChartSettings({...chartSettings, days: parseInt(e.target.value)})}
              style={{marginLeft: 8}}
            >
              <option value={3}>3 days</option>
              <option value={7}>7 days</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
            </select>
          </label>
          <label>
            <input 
              type="checkbox" 
              checked={chartSettings.showTrends}
              onChange={e => setChartSettings({...chartSettings, showTrends: e.target.checked})}
            />
            Show Trends
          </label>
          <label>
            <input 
              type="checkbox" 
              checked={chartSettings.showPipelinePerformance}
              onChange={e => setChartSettings({...chartSettings, showPipelinePerformance: e.target.checked})}
            />
            Show Pipeline Performance
          </label>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12, marginTop:12}}>
        <SuccessFailureChart days={chartSettings.days} />
        <AvgBuildTimeChart days={chartSettings.days} />
      </div>

      {/* Additional Charts */}
      {chartSettings.showTrends && (
        <div style={{marginTop: 12}}>
          <BuildTrendsChart days={chartSettings.days} />
        </div>
      )}

      {chartSettings.showPipelinePerformance && (
        <div style={{marginTop: 12}}>
          <PipelinePerformanceChart limit={15} />
        </div>
      )}

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
                {selectedBuild.duration_seconds && (
                  <div className="sub-value">
                    Duration: {Math.round(selectedBuild.duration_seconds)}s
                  </div>
                )}
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
