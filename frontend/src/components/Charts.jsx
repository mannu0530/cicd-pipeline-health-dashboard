
import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts'

export function SuccessFailureChart({ data }){
  // data: [{time: '10:00', success: 5, failed:2}, ...]
  return (
    <div className="card" style={{height:220}}>
      <div className="label">Success / Failure (recent)</div>
      <ResponsiveContainer width="100%" height="180">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="success" name="Success" />
          <Bar dataKey="failed" name="Failed" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function AvgBuildTimeChart({ data }){
  // data: [{time:'10:00', avg:120}, ...]
  return (
    <div className="card" style={{height:220}}>
      <div className="label">Avg Build Time (s)</div>
      <ResponsiveContainer width="100%" height="180">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="avg" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
