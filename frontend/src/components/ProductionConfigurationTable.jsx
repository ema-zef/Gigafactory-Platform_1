import { useState } from "react";
import axios from "axios";

export default function ProductionConfigurationTable({
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

  const scrollStyle = { maxHeight: "70vh", overflow: "auto", position: "relative" };
  const tableStyle = { width: "max-content", minWidth: "100%", borderCollapse: "separate", borderSpacing: 0 };
  const stickyHeaderStyle = { position: "sticky", top: 0, zIndex: 3, background: "#173b73", color: "white" };
  const stickyCornerStyle = { ...stickyHeaderStyle, left: 0, zIndex: 5, minWidth: 80, boxShadow: "3px 0 6px -4px rgba(0,0,0,.45)" };
  const stickyFirstCellStyle = { position: "sticky", left: 0, zIndex: 2, background: "#fff", minWidth: 80, boxShadow: "3px 0 6px -4px rgba(0,0,0,.35)" };


  const startEdit = (row) => {

    setEditingId(row.id);

    setEditData(row);
  };

  const save = async (id) => {
    try {
      const payload = {};

      (columns ?? []).forEach((col) => {
        payload[col.column_name] =
          editData[col.column_name] === ""
            ? null
            : editData[col.column_name];
      });

      await axios.put(
        `${API}/production_configuration/${id}`,
        payload
      );

      setEditingId(null);
      await reload();
    } catch (err) {
      console.error(
        "Production configuration update failed:",
        err.response?.data || err
      );

      alert(
        err.response?.data?.detail ||
        "Failed to update production configuration."
      );
    }
  };

  const remove = async (id) => {

    await axios.delete(
      `${API}/production_configuration/${id}`
    );

    reload();
  };

  return (

<div className="table-wrapper" style={scrollStyle}>

    <table border="1" style={tableStyle}>

      <thead>

        <tr>

          <th style={stickyCornerStyle}>ID</th>

          {(columns  ?? []).map((col) => (

            <th style={stickyHeaderStyle} key={col.column_name}>
              {col.column_name}
            </th>

          ))}

          <th style={stickyHeaderStyle}>Actions</th>

        </tr>

      </thead>

      <tbody>

        {data.map((row) => (

          <tr key={row.id}>

            <td style={stickyFirstCellStyle}>{row.id}</td>

            {(columns  ?? []).map((col) => (

              <td
                key={col.column_name}
              >

                {editingId ===
                row.id ? (

                  <input
                    value={
                      editData[
                        col.column_name
                      ] ?? ""
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
                  disabled={row.read_only}
                  onClick={() =>
                    startEdit(row)
                  }
                >
                  Edit
                </button>

              )}

              <button
                disabled={row.read_only}
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
</div>
  );
}