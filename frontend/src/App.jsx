import { useEffect, useRef, useState } from 'react'
import Plotly from 'plotly.js-dist-min'
import axios from 'axios'

function App() {

  alert("NEW BUILD TEST")

  console.log(
    "Fetching from:",
    "https://gigafactory-platform-1.onrender.com/dwelling-time"
  )

  const plotRef = useRef(null)

  const [loading, setLoading] = useState(true)

  useEffect(() => {

    axios
      .get('https://gigafactory-platform-1.onrender.com/dwelling-time')
      .then((response) => {

        console.log("Response received:", response.data)

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

        window.dispatchEvent(new Event('resize'))

        setLoading(false)

      })
      .catch((error) => {

        console.error("Backend error:", error)

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