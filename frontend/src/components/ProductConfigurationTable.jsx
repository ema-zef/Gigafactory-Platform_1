import { useState } from "react";
import axios from "axios";

export default function ProductConfigurationTable({
  data,
  columns,
  reload,
}) {

  const [editingId, setEditingId] =
    useState(null);

  const [editData, setEditData] =
    useState({});

  const API =
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000";

  const startEdit = (row) => {

    setEditingId(row.id);

    setEditData(row);
  };

  const save = async (id) => {

    await axios.put(
      `${API}/product_configuration/${id}`,
      editData
    );

    setEditingId(null);

    reload();
  };

  const remove = async (id) => {

    await axios.delete(
      `${API}/product_configuration/${id}`
    );

    reload();
  };

  return (

    <table border="1">

      <thead>

        <tr>

          <th>ID</th>

          {columns.map((col) => (

            <th key={col.column_name}>
              {col.column_name}
            </th>

          ))}

          <th>Actions</th>

        </tr>

      </thead>

      <tbody>

        {data.map((row) => (

          <tr key={row.id}>

            <td>{row.id}</td>

            {columns.map((col) => (

              <td
                key={col.column_name}
              >

                {editingId ===
                row.id ? (

                  <input
                    value={
                      editData[
                        col.column_name
                      ] || ""
                    }
                    onChange={(e) =>
                      setEditData({
                        ...editData,
                        [col.column_name]:
                          e.target.value,
                      })
                    }
                  />

                ) : (
                  row[col.column_name]
                )}

              </td>

            ))}

            <td>

              {editingId ===
              row.id ? (

                <button
                  onClick={() =>
                    save(row.id)
                  }
                >
                  Save
                </button>

              ) : (

                <button
                  onClick={() =>
                    startEdit(row)
                  }
                >
                  Edit
                </button>

              )}

              <button
                onClick={() =>
                  remove(row.id)
                }
              >
                Delete
              </button>

            </td>

          </tr>

        ))}

      </tbody>

    </table>
  );
}