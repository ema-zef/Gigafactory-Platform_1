import { useEffect, useState } from "react";
import axios from "axios";

import ProductionConfigurationForm
  from "./ProductionConfigurationForm";

import ProductionConfigurationTable
  from "./ProductionConfigurationTable";

export default function ProductionConfigurationManager() {

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
          `${API}/production_configuration`
        );

      const schemaResponse =
        await axios.get(
          `${API}/production_configuration/check`
        );

      setRecords(dataResponse.data || []);

      console.log("Schema received:", schemaResponse.data);

const filteredColumns =
  schemaResponse.data.columns.filter(
    c =>
      c.column_name !== "id" &&
      c.column_name !== "seq"
  );

console.log("Filtered columns:", filteredColumns);

setColumns(filteredColumns);


    } catch (error) {

      console.error(
        "Production Configuration load error:",
        error
      );

    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div>

      <h2>
        Production Configuration
      </h2>

      <button
        onClick={() =>
          setShowAdd(!showAdd)
        }
      >
        {showAdd
          ? "▼ Hide Form"
          : "► Add Production Configuration"}
      </button>

      {showAdd && (

        <ProductionConfigurationForm
          columns={columns}
          endpoint="production_configuration"
          reload={loadData}
        />

      )}

      <br />
      <br />

      <button
        onClick={() =>
          setShowTable(!showTable)
        }
      >
        {showTable
          ? "▼ Hide Table"
          : "► View Production Configurations"}
      </button>

      {showTable && (

        <ProductionConfigurationTable
          data={records}
          columns={columns}
          endpoint="production_configuration"
          reload={loadData}
        />

      )}

    </div>
  );
}