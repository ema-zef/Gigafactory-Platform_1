import { useState, useEffect } from "react";
import axios from "axios";

import PlotChart from "./components/PlotChart";
import EquipmentManager from "./components/EquipmentManager";
import EquipmentPalette from "./components/EquipmentPalette";
import EquipmentFlow from "./components/EquipmentFlow";
import ProductConfigurationManager from "./components/ProductConfigurationManager";
import ProductionConfigurationManager from "./components/ProductionConfigurationManager";

function App() {

  const API =
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000";

  const [backendStatus, setBackendStatus] =
    useState("Checking...");

  const [activeTab, setActiveTab] =
    useState("equipment");

  // ----------------------------------
  // Modeling Platform State
  // ----------------------------------

  const [plantOptions, setPlantOptions] =
    useState([]);

  const [productOptions, setProductOptions] =
    useState([]);

  const [selectedPlant, setSelectedPlant] =
    useState("");

  const [selectedProduct, setSelectedProduct] =
    useState("");

  const [targetOutput, setTargetOutput] =
    useState(1000);

  const [simulationResults, setSimulationResults] =
    useState([]);

  const [sessionId, setSessionId] =
    useState("");

  // ----------------------------------
  // Load dropdown values
  // ----------------------------------

  useEffect(() => {

    const loadOptions = async () => {

  try {

    const plantResponse =
      await axios.get(
        `${API}/production_configuration/options`
      );

    const productResponse =
      await axios.get(
        `${API}/product_configuration/options`
      );

    console.log(
      "Plant Options:",
      plantResponse.data
    );

    console.log(
      "Product Options:",
      productResponse.data
    );

    setPlantOptions(
      plantResponse.data
    );

    setProductOptions(
      productResponse.data
    );

  } catch (error) {

    console.error(
      "Failed loading options",
      error
    );

  }

};
    loadOptions();

  }, []);

  // ----------------------------------
  // Run Simulation
  // ----------------------------------

  const runSimulation = async () => {

    try {

      // Create temporary session

      const sessionResponse =
        await axios.post(
          `${API}/simulation_session`,
          {
            plant_code:
              selectedPlant,

            product_code:
              selectedProduct,

            target_output:
              targetOutput
          }
        );

      setSessionId(
        sessionResponse.data.session_id
      );

      // Run simulation

      const response =
        await axios.post(
          `${API}/simulate`,
          {
            plant_code:
              selectedPlant,

            product_code:
              selectedProduct,

            target_output:
              targetOutput
          }
        );

      setSimulationResults(
        response.data.simulation || []
      );

    } catch (error) {

      console.error(
        "Simulation error",
        error
      );

      alert(
        "Simulation failed"
      );

    }

  };

  // ----------------------------------
  // Save Simulation
  // ----------------------------------

  const saveSimulation = async () => {

    if (!sessionId) {

      alert(
        "Run simulation first"
      );

      return;
    }

    try {

      await axios.post(
        `${API}/save_simulation/${sessionId}`
      );

      alert(
        "Simulation saved"
      );

    } catch (error) {

      console.error(error);

      alert(
        "Failed to save simulation"
      );

    }

  };

  // ----------------------------------
  // Backend Status Color
  // ----------------------------------

  const statusColor =
    backendStatus === "Connected"
      ? "green"
      : backendStatus === "Disconnected"
      ? "red"
      : "orange";

  // ----------------------------------
  // UI
  // ----------------------------------

  return (

    <div style={{ padding: "20px" }}>

      <h1>
        Gigafactory Digital Twin
      </h1>

      <div
        style={{
          color: statusColor,
          fontWeight: "bold",
          marginBottom: "20px"
        }}
      >
        Backend: {backendStatus}
      </div>

      {/* Navigation */}

      <div
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "20px"
        }}
      >

        <button
          onClick={() =>
            setActiveTab("equipment")
          }
        >
          Equipment
        </button>

        <button
          onClick={() =>
            setActiveTab("product")
          }
        >
          Product Configuration
        </button>

        <button
          onClick={() =>
            setActiveTab("production")
          }
        >
          Production Configuration
        </button>

        <button
          onClick={() =>
            setActiveTab("digitalTwin")
          }
        >
          Modeling Platform
        </button>

        <button
          onClick={() =>
            setActiveTab("analytics")
          }
        >
          Analytics
        </button>

      </div>

      {/* Equipment */}

      {activeTab === "equipment" && (
        <EquipmentManager />
      )}

      {/* Product Configuration */}

      {activeTab === "product" && (

        <div>

          <h2>
            Product Configuration
          </h2>

          <ProductConfigurationManager />

        </div>

      )}

      {/* Production Configuration */}

      {activeTab === "production" && (

        <div>

          <h2>
            Production Configuration
          </h2>

          <ProductionConfigurationManager />

        </div>

      )}

      {/* Modeling Platform */}

      {activeTab === "digitalTwin" && (

        <div>

          <h2>
            Modeling Platform
          </h2>

          {/* Controls */}

          <div
            style={{
              display: "flex",
              gap: "10px",
              marginBottom: "20px",
              alignItems: "center",
              flexWrap: "wrap"
            }}
          >

            <select
              value={selectedPlant}
              onChange={(e) =>
                setSelectedPlant(
                  e.target.value
                )
              }
            >
              <option value="">
                Select Plant
              </option>

              {plantOptions.map(
                (plant) => (

                  <option
                    key={plant}
                    value={plant}
                  >
                    {plant}
                  </option>

                )
              )}

            </select>

            <select
              value={selectedProduct}
              onChange={(e) =>
                setSelectedProduct(
                  e.target.value
                )
              }
            >
              <option value="">
                Select Product
              </option>

              {productOptions.map(
                (product) => (

                  <option
                    key={product}
                    value={product}
                  >
                    {product}
                  </option>

                )
              )}

            </select>

            <input
              type="number"
              value={targetOutput}
              onChange={(e) =>
                setTargetOutput(
                  Number(
                    e.target.value
                  )
                )
              }
            />

            <button
              onClick={runSimulation}
            >
              Run Simulation
            </button>

            <button
              onClick={saveSimulation}
            >
              Save Simulation
            </button>

          </div>

          {/* Flow Layout */}

          <div
            style={{
              display: "flex",
              height: "700px"
            }}
          >

            <EquipmentPalette
              equipment={[]}
            />

            <div
              style={{
                flex: 1
              }}
            >
              <EquipmentFlow />
            </div>

          </div>

          {/* Results */}

          <div
            style={{
              marginTop: "20px"
            }}
          >

            <h3>
              Simulation Results
            </h3>

            {simulationResults.length > 0 ? (

              <table
                border="1"
                cellPadding="8"
                style={{
                  borderCollapse:
                    "collapse",
                  width: "100%"
                }}
              >

                <thead>

                  <tr>

                    <th>
                      Process
                    </th>

                    <th>
                      Required Output
                    </th>

                    <th>
                      Required Input
                    </th>

                    <th>
                      Quality Rate
                    </th>

                  </tr>

                </thead>

                <tbody>

                  {simulationResults.map(
                    (
                      row,
                      index
                    ) => (

                      <tr
                        key={index}
                      >

                        <td>
                          {row.process_name}
                        </td>

                        <td>
                          {row.required_output}
                        </td>

                        <td>
                          {row.required_input}
                        </td>

                        <td>
                          {row.quality_rate}
                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            ) : (

              <p>
                No simulation run yet.
              </p>

            )}

          </div>

        </div>

      )}

      {/* Analytics */}

      {activeTab === "analytics" && (

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit,minmax(500px,1fr))",
            gap: "20px",
            marginTop: "20px"
          }}
        >

          <PlotChart
            endpoint="/dwelling-time"
            title="Dwelling Time vs Solid Content"
            xLabel="Solid Content (w%)"
            yLabel="Dwelling Time (minutes)"
            setBackendStatus={
              setBackendStatus
            }
          />

          <PlotChart
            endpoint="/dwelling-time"
            title="Dwelling Time vs Electrode Thickness"
            xLabel="Electrode Thickness"
            yLabel="Dwelling Time"
            setBackendStatus={
              setBackendStatus
            }
          />

        </div>

      )}

    </div>

  );

}

export default App;