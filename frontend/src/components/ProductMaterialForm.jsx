import { useState } from "react";
import axios from "axios";
import "./FormLayout.css";

export default function ProductMaterialForm({
  columns,
  reload,
}) {

  const [formData, setFormData] = useState({});

  const API =
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000";

  const save = async () => {

    await axios.post(
      `${API}/product_material`,
      formData
    );

    setFormData({});

    reload();
  };

console.log("Columns:", columns);

  return (

    <>

      <div className="form-grid">

        {columns.map((column) => (

          <div
            key={column.column_name}
            className="form-group"
          >

            <label>
              {column.column_name
                .replaceAll("_", " ")
                .replace(/\b\w/g, c => c.toUpperCase())}
            </label>

            <input
              value={
                formData[column.column_name] || ""
              }

              onChange={(e) =>
                setFormData({
                  ...formData,
                  [column.column_name]:
                    e.target.value,
                })
              }
            />

          </div>

        ))}

      </div>

      <div className="form-actions">

        <button
          className="primary-button"
          onClick={save}
        >
          Save Product Material
        </button>

      </div>

    </>

  );

}