import React, { useState, useEffect } from 'react'
import { fetchBuildTrends, fetchPipelinePerformance } from '../api'

export default function BuildStats() {
  const [trends, setTrends] = useState([])
  const [pipelineStats, setPipelineStats] = useState([])
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState(14)

  useEffect(() => {
    async function loadStats() {
      setLoading(true)
      try {
        const [trendsData, pipelineData] = await Promise.all([
          fetchBuildTrends(timeRange),
          fetchPipelinePerformance(10)
        ])
        setTrends(trendsData)
        setPipelineStats(pipelineData)
      } catch (error) {
        console.error('Error loading stats:', error)
      } finally {
        setLoading(false)
      }
    }
    
    loadStats()
  }, [timeRange])

  const formatDuration = (seconds) => {
    if (!seconds) return '—'
    if (seconds < 60) return `${Math.round(seconds)}s`
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`
    return `${Math.round(seconds / 3600)}h ${Math.round((seconds % 3600) / 60)}m`
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  if (loading) {
    return (
      <div className="card">
        <div className="label">Build Statistics</div>
        <div style={{ textAlign: 'center', padding: '20px', color: 'var(--muted)' }}>
          Loading statistics...
        </div>
      </div>
    )
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
      {/* Build Trends Summary */}
      <div className="card">
        <div className="label">Build Trends (Last {timeRange} days)</div>
        <div style={{ marginBottom: '16px' }}>
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(parseInt(e.target.value))}
            style={{ 
              background: 'var(--bg)', 
              border: '1px solid var(--border)', 
              color: 'var(--text)', 
              padding: '4px 8px', 
              borderRadius: '4px' 
            }}
          >
            <option value={7}>7 days</option>
            <option value={14}>14 days</option>
            <option value={30}>30 days</option>
          </select>
        </div>
        
        {trends.length > 0 ? (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '16px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--success)' }}>
                  {trends.reduce((sum, t) => sum + t.success_count, 0)}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Total Success</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--failure)' }}>
                  {trends.reduce((sum, t) => sum + t.failure_count, 0)}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Total Failed</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--primary)' }}>
                  {Math.round(trends.reduce((sum, t) => sum + t.avg_duration, 0) / trends.length)}s
                </div>
                <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Avg Duration</div>
              </div>
            </div>
            
            <div style={{ fontSize: '12px', color: 'var(--muted)' }}>
              Recent trend: {trends.slice(-3).map(t => formatDate(t.date)).join(' → ')}
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--muted)', fontSize: '14px' }}>
            No trend data available
          </div>
        )}
      </div>

      {/* Top Performing Pipelines */}
      <div className="card">
        <div className="label">Top Performing Pipelines</div>
        {pipelineStats.length > 0 ? (
          <div>
            {pipelineStats.slice(0, 5).map((pipeline, index) => (
              <div 
                key={pipeline.pipeline_name}
                style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '8px 0',
                  borderBottom: index < 4 ? '1px solid var(--border)' : 'none'
                }}
              >
                <div>
                  <div style={{ fontSize: '14px', fontWeight: '500' }}>
                    {pipeline.pipeline_name}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--muted)' }}>
                    {pipeline.total_builds} builds
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ 
                    fontSize: '16px', 
                    fontWeight: 'bold',
                    color: pipeline.success_rate >= 90 ? 'var(--success)' : 
                           pipeline.success_rate >= 75 ? 'var(--warning)' : 'var(--failure)'
                  }}>
                    {pipeline.success_rate}%
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--muted)' }}>
                    {formatDuration(pipeline.avg_duration)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--muted)', fontSize: '14px' }}>
            No pipeline data available
          </div>
        )}
      </div>
    </div>
  )
}

