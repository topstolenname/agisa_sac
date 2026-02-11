// Figure 7 – Consciousness Metrics Dashboard (React + Recharts template)
// Usage: Import into your docs site or a demo app. Requires Recharts.
// npm install recharts
import React from 'react';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const sampleData = [
  { time: 0, phi: 0.2, recursion: 1, coherence: 0.6, memory: 0.1 },
  { time: 1, phi: 0.25, recursion: 1, coherence: 0.62, memory: 0.15 },
  { time: 2, phi: 0.31, recursion: 2, coherence: 0.64, memory: 0.22 },
  { time: 3, phi: 0.37, recursion: 2, coherence: 0.67, memory: 0.28 },
  { time: 4, phi: 0.42, recursion: 3, coherence: 0.70, memory: 0.35 },
  { time: 5, phi: 0.44, recursion: 3, coherence: 0.72, memory: 0.41 }
];

export default function ConsciousnessDashboard({ data = sampleData }) {
  return (
    <div style={{ width: '100%', height: 360 }}>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          {/* Do not fix colors; let theme handle them */}
          <Line type="monotone" dataKey="phi" dot={false} />
          <Line type="monotone" dataKey="recursion" dot={false} />
          <Line type="monotone" dataKey="coherence" dot={false} />
          <Line type="monotone" dataKey="memory" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}