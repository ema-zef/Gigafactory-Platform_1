import { useEffect, useRef, useState } from 'react'
import Plotly from 'plotly.js-dist-min'
import axios from 'axios'

function App() {

  const plotRef = useRef(null)

  const [loading, setLoading] = useState(true)

  useEffect(() => {

    console.log(
      "Fetching from:",
      "https://gigafactory-platform-1.onrender.com/dwelling-time"
    )

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
            },
            margin: {
              l: 80,
              r: 40,
              t: 60,
              b: 80
            }
          },
          {
            responsive: true
          }
        ).then(() => {

          Plotly.Plots.resize(plotRef.current)

          console.log("Plot rendered successfully")

          setLoading(false)

        })

      })
      .catch((error) => {

        console.error("Backend error:", error)

        setLoading(false)

        alert('Backend connection failed')

      })

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

      <p>Graph container below:</p>

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