import { useEffect, useRef, useState } from 'react'
import Plotly from 'plotly.js-dist-min'
import axios from 'axios'

function App() {

  console.log("API URL =", import.meta.env.VITE_API_URL)

  const plotRef = useRef(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {

    axios
      .get('https://gigafactory-platform-1.onrender.com/dwelling-time')
      .then((response) => {

        Plotly.newPlot(
          plotRef.current,
          [
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
          ],
          {
            title: 'Dwelling Time vs Solid Content',
            autosize: true,
            xaxis: {
              title: 'Solid Content (w%)'
            },
            yaxis: {
              title: 'Dwelling Time (minutes)'
            }
          },
          {
            responsive: true
          }
        )

        setLoading(false)

        setTimeout(() => {
          if (plotRef.current) {
            Plotly.Plots.resize(plotRef.current)
          }
        }, 500)

      })
      .catch((error) => {

        console.error(error)

        alert('Backend connection failed')

      })

  }, [])

  return (
    <div style={{ padding: '40px' }}>

      <h1>Scientific Dashboard</h1>

      {loading && <p>Loading graph...</p>}

      <div
        ref={plotRef}
        style={{
          width: '100%',
          height: '600px',
          minHeight: '600px'
        }}
      />

    </div>
  )
}

export default App