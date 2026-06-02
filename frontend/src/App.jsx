import { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'
import axios from 'axios'

function App() {

  const [loading, setLoading] = useState(true)
  const [plotData, setPlotData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {

    let mounted = true

    console.log(
      "Fetching from:",
      "https://gigafactory-platform-1.onrender.com/dwelling-time"
    )

    axios
      .get('https://gigafactory-platform-1.onrender.com/dwelling-time')
      .then((response) => {

        if (!mounted) return

        console.log("Response received:", response.data)

        setPlotData([
          {
            x: response.data.x,
            y: response.data.y,
            type: 'scatter',
            mode: 'lines',
            line: {
              color: 'blue',
              width: 3
            }
          }
        ])

        setLoading(false)

      })
      .catch((error) => {

        console.error("Backend error:", error)

        if (!mounted) return

        setError('Backend connection failed')
        setLoading(false)

      })

    return () => {
      mounted = false
    }

  }, [])

  return (
    <div
      style={{
        padding: '40px',
        width: '100%',
        maxWidth: '1200px',
        margin: '0 auto'
      }}
    >
      <h1>Scientific Dashboard</h1>

      {loading && <p>Loading graph...</p>}

      {error && (
        <p style={{ color: 'red' }}>
          {error}
        </p>
      )}

      {!loading && plotData && (
        <Plot
          data={plotData}
          layout={{
            title: 'Dwelling Time vs Solid Content',
            autosize: true,
            xaxis: {
              title: 'Solid Content (w%)'
            },
            yaxis: {
              title: 'Dwelling Time (minutes)'
            },
            margin: {
              l: 80,
              r: 40,
              t: 60,
              b: 80
            }
          }}
          config={{
            responsive: true
          }}
          useResizeHandler={true}
          style={{
            width: '100%',
            height: '700px',
            border: '1px solid #cccccc',
            backgroundColor: '#ffffff'
          }}
        />
      )}
    </div>
  )
}

export default App