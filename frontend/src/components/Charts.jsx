
import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, AreaChart, Area, PieChart, Pie, Cell } from 'recharts'
import { fetchChartData, fetchBuildTrends, fetchPipelinePerformance } from '../api'

export function SuccessFailureChart({ data, days = 7 }){
  const [chartData, setChartData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadChartData() {
      setLoading(true)
      try {
        const apiData = await fetchChartData(days)
        if (apiData && apiData.length > 0) {
          setChartData(apiData)
        } else {
          // Fallback to provided data or generate sample data
          setChartData(data || generateFallbackData(days))
        }
      } catch (error) {
        console.error('Error loading chart data:', error)
        setChartData(data || generateFallbackData(days))
      } finally {
        setLoading(false)
      }
    }
    
    loadChartData()
  }, [days, data])

  const generateFallbackData = (count) => {
    return Array.from({length: count}, (_, i) => ({
      time: `Day ${i+1}`,
      success: Math.floor(Math.random() * 8) + 2,
      failed: Math.floor(Math.random() * 3),
      running: Math.floor(Math.random() * 2)
    }))
  }

  if (loading) {
    return (
      <div className="card" style={{height: 220}}>
        <div className="label">Success / Failure / Running (recent {days} days)</div>
        <div style={{
          height: 180,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--muted)',
          fontSize: '14px'
        }}>
          Loading...
        </div>
      </div>
    )
  }

  return (
    <div className="card" style={{height: 220}}>
      <div className="label">Success / Failure / Running (recent {days} days)</div>
      {chartData && chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height="180">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => [value, name === 'success' ? 'Success' : name === 'failed' ? 'Failed' : 'Running']}
              labelStyle={{ color: 'var(--text)' }}
            />
            <Legend />
            <Bar dataKey="success" name="Success" fill="#1bc47d" stackId="a" />
            <Bar dataKey="failed" name="Failed" fill="#ef476f" stackId="a" />
            <Bar dataKey="running" name="Running" fill="#ffd23f" stackId="a" />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div style={{
          height: 180,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--muted)',
          fontSize: '14px'
        }}>
          No data available
        </div>
      )}
    </div>
  )
}

export function AvgBuildTimeChart({ data, days = 7 }){
  const [chartData, setChartData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadChartData() {
      setLoading(true)
      try {
        const apiData = await fetchChartData(days)
        if (apiData && apiData.length > 0) {
          setChartData(apiData)
        } else {
          setChartData(data || generateFallbackData(days))
        }
      } catch (error) {
        console.error('Error loading chart data:', error)
        setChartData(data || generateFallbackData(days))
      } finally {
        setLoading(false)
      }
    }
    
    loadChartData()
  }, [days, data])

  const generateFallbackData = (count) => {
    return Array.from({length: count}, (_, i) => ({
      time: `Day ${i+1}`,
      avg_duration: Math.floor(Math.random() * 1200) + 300
    }))
  }

  if (loading) {
    return (
      <div className="card" style={{height: 220}}>
        <div className="label">Average Build Time (recent {days} days)</div>
        <div style={{
          height: 180,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--muted)',
          fontSize: '14px'
        }}>
          Loading...
        </div>
      </div>
    )
  }

  return (
    <div className="card" style={{height: 220}}>
      <div className="label">Average Build Time (recent {days} days)</div>
      {chartData && chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height="180">
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip 
              formatter={(value) => [`${Math.round(value)}s`, 'Duration']}
              labelStyle={{ color: 'var(--text)' }}
            />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="avg_duration" 
              stroke="#8884d8" 
              fill="#8884d8" 
              fillOpacity={0.3}
              strokeWidth={2} 
            />
          </AreaChart>
        </ResponsiveContainer>
      ) : (
        <div style={{
          height: 180,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--muted)',
          fontSize: '14px'
        }}>
          No data available
        </div>
      )}
    </div>
  )
}

export function BuildTrendsChart({ days = 14 }){
  const [chartData, setChartData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadTrendData() {
      setLoading(true)
      try {
        const apiData = await fetchBuildTrends(days)
        setChartData(apiData)
      } catch (error) {
        console.error('Error loading trend data:', error)
        setChartData([])
      } finally {
        setLoading(false)
      }
    }
    
    loadTrendData()
  }, [days])

  if (loading) {
    return (
      <div className="card" style={{height: 220}}>
        <div className="label">Build Trends (last {days} days)</div>
        <div style={{
          height: 180,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--muted)',
          fontSize: '14px'
        }}>
          Loading...
        </div>
      </div>
    )
  }

  return (
    <div className="card" style={{height: 220}}>
      <div className="label">Build Trends (last {days} days)</div>
      {chartData && chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height="180">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => [
                name === 'total_builds' ? value : name === 'avg_duration' ? `${Math.round(value)}s` : value,
                name === 'total_builds' ? 'Total Builds' : name === 'success_count' ? 'Success' : name === 'failure_count' ? 'Failed' : 'Avg Duration'
              ]}
              labelStyle={{ color: 'var(--text)' }}
            />
            <Legend />
            <Line type="monotone" dataKey="total_builds" stroke="#8884d8" strokeWidth={2} name="Total Builds" />
            <Line type="monotone" dataKey="success_count" stroke="#1bc47d" strokeWidth={2} name="Success" />
            <Line type="monotone" dataKey="failure_count" stroke="#ef476f" strokeWidth={2} name="Failed" />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div style={{
          height: 180,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--muted)',
          fontSize: '14px'
        }}>
          No trend data available
        </div>
      )}
    </div>
  )
}

export function PipelinePerformanceChart({ limit = 10 }){
  const [chartData, setChartData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadPipelineData() {
      setLoading(true)
      try {
        const apiData = await fetchPipelinePerformance(limit)
        setChartData(apiData)
      } catch (error) {
        console.error('Error loading pipeline data:', error)
        setChartData([])
      } finally {
        setLoading(false)
      }
    }
    
    loadPipelineData()
  }, [limit])

  if (loading) {
    return (
      <div className="card" style={{height: 220}}>
        <div className="label">Pipeline Performance (Top {limit})</div>
        <div style={{
          height: 180,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--muted)',
          fontSize: '14px'
        }}>
          Loading...
        </div>
      </div>
    )
  }

  return (
    <div className="card" style={{height: 220}}>
      <div className="label">Pipeline Performance (Top {limit})</div>
      {chartData && chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height="180">
          <BarChart data={chartData} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="pipeline_name" type="category" width={80} />
            <Tooltip 
              formatter={(value, name) => [
                name === 'success_rate' ? `${value}%` : name === 'avg_duration' ? `${Math.round(value)}s` : value,
                name === 'total_builds' ? 'Total Builds' : name === 'success_rate' ? 'Success Rate' : 'Avg Duration'
              ]}
              labelStyle={{ color: 'var(--text)' }}
            />
            <Legend />
            <Bar dataKey="success_rate" name="Success Rate" fill="#1bc47d" />
            <Bar dataKey="avg_duration" name="Avg Duration" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div style={{
          height: 180,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--muted)',
          fontSize: '14px'
        }}>
          No pipeline data available
        </div>
      )}
    </div>
  )
}
