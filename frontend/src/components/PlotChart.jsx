import { useEffect, useRef, useState } from 'react'
import Plotly from 'plotly.js-dist-min'
import axios from 'axios'

function PlotChart({ endpoint, title, xLabel, yLabel, setBackendStatus }) {

  const plotRef = useRef(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {

    const handleResize = () => {
      if (plotRef.current) {
        Plotly.Plots.resize(plotRef.current)
      }
    }

    window.addEventListener('resize', handleResize)

    axios
      .get(`${import.meta.env.VITE_API_URL}${endpoint}`)
      .then((response) => {

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
              text: title,
              font: {
                size: 28
              }
            },

            autosize: true,

            xaxis: {
              title: {
                text: xLabel,
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
                text: yLabel,
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
console.log('Setting loading to false')

        setLoading(false)

requestAnimationFrame(() => {
  if (plotRef.current) {
    Plotly.Plots.resize(plotRef.current)
  }
})

setTimeout(() => {
  if (plotRef.current) {
    Plotly.Plots.resize(plotRef.current)
  }
}, 500)

setTimeout(() => {
  if (plotRef.current) {
    Plotly.Plots.resize(plotRef.current)
  }
}, 1500)

        setTimeout(() => {
          if (plotRef.current) {
            Plotly.Plots.resize(plotRef.current)
          }
        }, 300)

      })
      .catch((error) => {

        console.error(error)

        setBackendStatus('Disconnected')

        setLoading(false)

      })

    return () => {

      window.removeEventListener('resize', handleResize)

      if (plotRef.current) {
        Plotly.purge(plotRef.current)
      }

    }

  }, [endpoint, title, xLabel, yLabel, setBackendStatus])

  return (
    <>
      {loading && (
        <div
          style={{
            textAlign: 'center',
            padding: '20px',
            fontSize: '18px'
          }}
        >
          ⏳ Loading graph...
        </div>
      )}

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
    </>
  )
}

export default PlotChart