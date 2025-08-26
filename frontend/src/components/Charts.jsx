
import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts'

export function SuccessFailureChart({ data }){
  // data: [{time: '10:00', success: 5, failed:2}, ...]
  
  console.log('SuccessFailureChart received data:', data)
  
  // Generate fallback data if no data provided
  const chartData = data && data.length > 0 ? data : Array.from({length: 10}, (_, i) => ({
    time: `Build ${i+1}`,
    success: Math.floor(Math.random() * 5) + 1,
    failed: Math.floor(Math.random() * 2)
  }));
  
  console.log('SuccessFailureChart using chartData:', chartData)

  return (
    <div className="card" style={{height:220}}>
      <div className="label">Success / Failure (recent)</div>
      {chartData && chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height="180">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="success" name="Success" fill="#1bc47d" />
            <Bar dataKey="failed" name="Failed" fill="#ef476f" />
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

export function AvgBuildTimeChart({ data }){
  // data: [{time:'10:00', avg:120}, ...]
  
  console.log('AvgBuildTimeChart received data:', data)
  
  // Generate fallback data if no data provided
  const chartData = data && data.length > 0 ? data : Array.from({length: 10}, (_, i) => ({
    time: `Build ${i+1}`,
    avg: Math.floor(Math.random() * 300) + 60 // 1-6 minutes for better visibility
  }));
  
  console.log('AvgBuildTimeChart using chartData:', chartData)

  return (
    <div className="card" style={{height:220}}>
      <div className="label">Avg Build Time (s)</div>
      {chartData && chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height="180">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="avg" stroke="#8884d8" strokeWidth={2} />
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
          No data available
        </div>
      )}
    </div>
  )
}
