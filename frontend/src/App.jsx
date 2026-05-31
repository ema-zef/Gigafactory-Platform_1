import { useEffect, useRef, useState } from 'react'
import Plotly from 'plotly.js-dist-min'
import axios from 'axios'

function App() {

  console.log("API URL =", import.meta.env.VITE_API_URL)

  const plotRef = useRef(null)

  const [loading, setLoading] = useState(true)

  useEffect(() => {

    axios
      .get(`${import.meta.env.VITE_API_URL}/dwelling-time`)
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
            width: 900,
            height: 500,
            xaxis: {
              title: 'Solid Content (w%)'
            },
            yaxis: {
              title: 'Dwelling Time (minutes)'
            }
          }
        )

        setLoading(false)

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

      <div ref={plotRef}></div>

    </div>
  )
}

export default App