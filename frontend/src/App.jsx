import { useState } from "react";
import PlotChart from "./components/PlotChart";
import GigafactoryFlow from "./components/GigafactoryFlow";

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking...");

  const statusColor =
    backendStatus === "Connected"
      ? "green"
      : backendStatus === "Disconnected"
      ? "red"
      : "orange";

  return (
    <div style={{ padding: "20px" }}>
      <h1>Gigafactory Digital Twin</h1>

      <div
        style={{
          color: statusColor,
          fontWeight: "bold",
          marginBottom: "20px",
        }}
      >
        Backend: {backendStatus}
      </div>

      {/* Factory Flow on top */}
      <div style={{ marginBottom: "40px" }}>
        <GigafactoryFlow />
      </div>

      {/* Graphs below */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(500px, 1fr))",
          gap: "20px",
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
          title="Dwelling Time vs Electrode Thickness"
          xLabel="Electrode Thickness"
          yLabel="Dwelling Time"
          setBackendStatus={setBackendStatus}
        />
      </div>
    </div>
  );
}

export default App;