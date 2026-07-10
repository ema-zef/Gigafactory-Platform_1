import { useEffect, useState } from "react";
import axios from "axios";

import ProductConfigurationForm
  from "./ProductConfigurationForm";

import ProductConfigurationTable
  from "./ProductConfigurationTable";

import SimulationResultsPanel
from "./SimulationResultsPanel";

export default function ProductConfigurationManager() {

  const [records, setRecords] =
    useState([]);

  const [columns, setColumns] =
    useState([]);

  const [showAdd, setShowAdd] =
    useState(false);

  const [showTable, setShowTable] =
    useState(false);

  const API =
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000";

  const loadData = async () => {

    try {

      const dataResponse =
        await axios.get(
          `${API}/product_configuration`
        );

      const schemaResponse =
        await axios.get(
          `${API}/product_configuration/check`
        );

      setRecords(dataResponse.data || []);

      setColumns(
        (schemaResponse.data.columns || [])
          .filter(
            (c) =>
              c.column_name !== "id"
          )
      );

    } catch (error) {

      console.error(
        "Product Configuration load error:",
        error
      );

    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
  <div>

    <h2
      style={{
        textAlign: "center",
        color: "#173b73",
        marginBottom: "25px"
      }}
    >
      Product Configuration
    </h2>

    <button
      onClick={() => setShowAdd(!showAdd)}
    >
      {showAdd
        ? "▼ Hide Form"
        : "► Add Product Configuration"}
    </button>

    {showAdd && (

      <div className="form-card">

        <div className="form-title">
          Add Product Configuration
        </div>

        <ProductConfigurationForm
          columns={columns}
          endpoint="product_configuration"
          reload={loadData}
        />

      </div>

    )}

    <br />
    <br />

    <button
      onClick={() => setShowTable(!showTable)}
    >
      {showTable
        ? "▼ Hide Table"
        : "► View Product Configurations"}
    </button>

    {showTable && (

      <ProductConfigurationTable
        data={records}
        columns={columns}
        endpoint="product_configuration"
        reload={loadData}
      />

    )}

  </div>
);
}