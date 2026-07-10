import { useState } from "react";
import axios from "axios";

export default function ProductMaterial({
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

    setEditingId(row.seq);

    setEditData(row);
  };

  const save = async (id) => {

    await axios.put(
      `${API}/product_material/${id}`,
      editData
    );

    setEditingId(null);

    reload();
  };

  const remove = async (id) => {

    await axios.delete(
      `${API}/product_material/${id}`
    );

    reload();
  };

  return (

<div className="table-wrapper">

    <table
    style={{
        width:"max-content",
        width: "100%",
        borderCollapse: "collapse",
        marginTop: "20px"
    }}
    >

            <thead
    style={{
        background: "#173b73",
        color: "white"
    }}
    >

        <tr>

          
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

          <tr key={row.seq}>

            
            {columns.map((col) => (

              <td
                key={col.column_name}
              >

                {editingId ===
                row.seq ? (

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
              row.seq ? (

                <button
                  onClick={() =>
                    save(row.seq)
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
                  remove(row.seq)
                }
              >
                Delete
              </button>

            </td>

          </tr>

        ))}

      </tbody>

    </table>
</div>
  );
}