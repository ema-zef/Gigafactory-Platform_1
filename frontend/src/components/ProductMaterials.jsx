import { useEffect, useState } from "react";
import axios from "axios";

import ProductMaterialForm from "./ProductMaterialForm";
import ProductMaterialTable from "./ProductMaterialTable";

import "./FormLayout.css";

export default function ProductMaterialManager() {

    const API =
        import.meta.env.VITE_API_URL ||
        "http://localhost:8000";

    const [records, setRecords] = useState([]);
    const [columns, setColumns] = useState([]);

    const [showAdd, setShowAdd] = useState(true);
    const [showTable, setShowTable] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {

  try {

    const schemaResponse = await axios.get(
      `${API}/product_material/check`
    );

    setColumns(
      schemaResponse.data.columns.filter(
        c => c.column_name !== "id"
      )
    );

  } catch (err) {

    console.error(
      "Schema error:",
      err
    );

  }

  try {

    const dataResponse = await axios.get(
      `${API}/product_material`
    );

    setRecords(dataResponse.data);

  } catch (err) {

    console.error(
      "Data error:",
      err
    );

    setRecords([]);

  }

};

console.log("Manager columns state:", columns);

    return (

        <div>

            <h2
                style={{
                    textAlign: "center",
                    color: "#173b73",
                    marginBottom: "25px"
                }}
            >
                Product Material Database
            </h2>

            <button
                onClick={() =>
                    setShowAdd(!showAdd)
                }
            >
                {showAdd
                    ? "▼ Hide Form"
                    : "► Add Product Material"}
            </button>

            {showAdd && (

                <div className="form-card">

                    <div className="form-title">

                        Add Product Material

                    </div>

                    <ProductMaterialForm
                        columns={columns}
                        reload={loadData}
                    />

                </div>

            )}

            <br />

            <button
                onClick={() =>
                    setShowTable(!showTable)
                }
            >
                {showTable
                    ? "▼ Hide Table"
                    : "► View Product Materials"}
            </button>

            {showTable && (

                <ProductMaterialTable
                    data={records}
                    columns={columns}
                    reload={loadData}
                />

            )}

        </div>

    );

}