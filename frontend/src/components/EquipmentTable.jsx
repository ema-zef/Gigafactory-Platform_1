export default function EquipmentTable({

columns,
equipment,

editingId,
editData,
setEditData,

startEdit,
updateEquipment,
deleteEquipment,

setEditingId

}) {

return (


<div
  style={{
    overflowX: "auto"
  }}
>

  <table
    border="1"
    cellPadding="5"
  >

    <thead>

      <tr>

        <th>ID</th>

        {columns.map(col => (

          <th
            key={col.column_name}
          >
            {col.column_name}
          </th>

        ))}

        <th>Actions</th>

      </tr>

    </thead>

    <tbody>

      {equipment.map(row => (

        <tr key={row.id}>

          <td>{row.id}</td>

          {columns.map(col => (

            <td key={col.column_name}>

              {editingId === row.id ? (

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
                        e.target.value
                    })
                  }
                />

              ) : (

                String(
                  row[col.column_name]
                  ?? ""
                )

              )}

            </td>

          ))}

          <td>

            {editingId === row.id ? (

              <>

                <button
                  onClick={() =>
                    updateEquipment(
                      row.id
                    )
                  }
                >
                  Save
                </button>

                <button
                  onClick={() =>
                    setEditingId(null)
                  }
                >
                  Cancel
                </button>

              </>

            ) : (

              <>

                <button
                  onClick={() =>
                    startEdit(row)
                  }
                >
                  Edit
                </button>

                <button
                  onClick={() =>
                    deleteEquipment(
                      row.id
                    )
                  }
                >
                  Delete
                </button>

              </>

            )}

          </td>

        </tr>

      ))}

    </tbody>

  </table>

</div>


);

}
