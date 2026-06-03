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
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))',
    gap: '20px'
  }}
>
  <PlotChart
    endpoint="/dwelling-time"
    title="Dwelling Time vs Solid Content"
    xLabel="Solid Content (w%)"
    yLabel="Dwelling Time (minutes)"
    setBackendStatus={setBackendStatus}
  />

  <PlotChart
    endpoint="/dwelling-time"
    title="Dwelling Time vs Elect. Thickness"
    xLabel="X"
    yLabel="Y"
    setBackendStatus={setBackendStatus}
  />
</div>
  )
}

export default App