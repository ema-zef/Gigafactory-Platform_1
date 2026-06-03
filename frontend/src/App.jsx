import { useState } from 'react'
import PlotChart from './components/PlotChart'

function App() {

  const [backendStatus, setBackendStatus] = useState('Checking...')

  const statusColor =
    backendStatus === 'Connected'
      ? 'green'
      : backendStatus === 'Disconnected'
      ? 'red'
      : 'orange'

  return (
    <div
      style={{
        padding: '40px',
        maxWidth: '1200px',
        margin: '0 auto'
      }}
    >

      <h1>Scientific Dashboard</h1>

      <p
        style={{
          color: statusColor,
          fontWeight: 'bold',
          fontSize: '18px'
        }}
      >
        Backend Status: {backendStatus}
      </p>

      <PlotChart
  endpoint="/dwelling-time"
  title="Dwelling Time vs Solid Content"
  xLabel="Solid Content (w%)"
  yLabel="Dwelling Time (minutes)"
  setBackendStatus={setBackendStatus}
/>

<PlotChart
  endpoint="/dwelling-time"
  title="Dwelling Time vs Electrode Thickness"
  xLabel="X"
  yLabel="Y"
  setBackendStatus={setBackendStatus}
/>

    </div>
  )
}

export default App