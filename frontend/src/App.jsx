import { useEffect, useRef, useState } from 'react'
import Plotly from 'plotly.js-dist-min'
import axios from 'axios'

function App() {

  const plotRef = useRef(null)

  const [loading, setLoading] = useState(true)
  const [backendStatus, setBackendStatus] = useState('Checking...')

  useEffect(() => {

    const handleResize = () => {
      if (plotRef.current) {
        Plotly.Plots.resize(plotRef.current)
      }
    }

    window.addEventListener('resize', handleResize)

    console.log(
      "Fetching from:",
      "https://gigafactory-platform-1.onrender.com/dwelling-time"
    )

    axios
      .get('https://gigafactory-platform-1.onrender.com/dwelling-time')
      .then((response) => {

        console.log("Response received:", response.data)

        setBackendStatus('Connected')

        return Plotly.newPlot(
          plotRef.current,
          [
            {
              x: response.data.x,
              y: response.data.y,
              type: 'scatter',
              mode: 'lines',
              line: {
                color: 'blue',
                width: 4
              }
            }
          ],
          {
            title: {
              text: 'Dwelling Time vs Solid Content',
              font: {
                size: 28
              }
            },

            autosize: true,

            xaxis: {
              title: {
                text: 'Solid Content (w%)',
                font: {
                  size: 20
                }
              },
              tickfont: {
                size: 16
              }
            },

            yaxis: {
              title: {
                text: 'Dwelling Time (minutes)',
                font: {
                  size: 20
                }
              },
              tickfont: {
                size: 16
              }
            },

            margin: {
              l: 90,
              r: 40,
              t: 80,
              b: 90
            }
          },
          {
            responsive: true
          }
        )
      })
      .then(() => {

        console.log("Plot rendered successfully")

        setLoading(false)

        requestAnimationFrame(() => {
          if (plotRef.current) {
            Plotly.Plots.resize(plotRef.current)
            console.log("Plot resized")
          }
        })

        setTimeout(() => {
          if (plotRef.current) {
            Plotly.Plots.resize(plotRef.current)
            console.log("Delayed resize completed")
          }
        }, 300)

      })
      .catch((error) => {

        console.error("Backend error:", error)

        setBackendStatus('Disconnected')

        setLoading(false)

      })

    return () => {
      window.removeEventListener('resize', handleResize)
    }

  }, [])

  return (
    <div
      style={{
        padding: '40px',
        maxWidth: '1200px',
        margin: '0 auto'
      }}
    >

      <h1>Scientific Dashboard</h1>

      <p>
        Backend Status: <strong>{backendStatus}</strong>
      </p>

      {loading && <p>Loading graph...</p>}

      <div
        ref={plotRef}
        style={{
          width: '100%',
          height: '700px',
          minHeight: '700px',
          border: '1px solid #cccccc',
          backgroundColor: '#ffffff'
        }}
      />

    </div>
  )
}

export default App