import { useState } from "react";
import axios from "axios";

export default function ProductConfigurationForm({
  columns,
  reload,
}) {

  const [formData, setFormData] =
    useState({});

  const API =
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000";

  const save = async () => {

    await axios.post(
      `${API}/product_configuration`,
      formData
    );

    setFormData({});

    reload();
  };

  return (

    <div>

      {columns.map((column) => (

        <div key={column.column_name}>

          <label>
            {column.column_name}
          </label>

          <input
            value={
              formData[
                column.column_name
              ] || ""
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

      <button onClick={save}>
        Save
      </button>

    </div>

  );
}