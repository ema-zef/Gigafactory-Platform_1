import { useEffect, useRef, useState } from 'react'
import Plotly from 'plotly.js-dist-min'
import axios from 'axios'

function App() {

  const plotRef = useRef(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {

    console.log("App mounted")

    console.log(
      "Fetching from:",
      "https://gigafactory-platform-1.onrender.com/dwelling-time"
    )

    axios
      .get('https://gigafactory-platform-1.onrender.com/dwelling-time')
      .then((response) => {

        alert("Backend returned data")

        console.log("Response received:", response.data)
        console.log("Plotly object:", Plotly)
        console.log("Plot ref:", plotRef.current)
        console.log("About to render plot")

        return Plotly.newPlot(
          plotRef.current,
          [
            {
              x: response.data.x,
              y: response.data.y,
              type: 'scatter',
              mode: 'markers+lines',
              marker: {
                size: 10
              },
              line: {
                color: 'blue',
                width: 5
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
                  size: 22
                }
              }
            },

            yaxis: {
              title: {
                text: 'Dwelling Time (minutes)',
                font: {
                  size: 22
                }
              }
            },

            margin: {
              l: 80,
              r: 40,
              t: 80,
              b: 80
            }
          },
          {
            responsive: true
          }
        )

      })
      .then(() => {

        alert("Plot rendered successfully")

        Plotly.Plots.resize(plotRef.current)

        console.log("Plot rendered successfully")

        setLoading(false)

      })
      .catch((error) => {

        console.error("Backend error:", error)

        alert(
          "ERROR:\n\n" +
          JSON.stringify(error?.message || error, null, 2)
        )

        setLoading(false)

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

      <div
        ref={plotRef}
        style={{
          width: '100%',
          height: '700px',
          border: '1px solid #ccc'
        }}
      />
    </div>
  )
}

export default App