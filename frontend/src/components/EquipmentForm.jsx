export default function EquipmentForm({
columns,
newEquipment,
setNewEquipment,
createEquipment
}) {

return (


<div>

  <h3>Add Equipment</h3>

  <div
    style={{
      display: "grid",
      gridTemplateColumns:
        "repeat(auto-fill,minmax(220px,1fr))",
      gap: "10px"
    }}
  >

    {columns.map(column => (

      <div key={column.column_name}>

        <label>
          {column.column_name}
        </label>

        <input
          value={
            newEquipment[
              column.column_name
            ] || ""
          }
          onChange={(e) =>
            setNewEquipment({
              ...newEquipment,
              [column.column_name]:
                e.target.value
            })
          }
        />

      </div>

    ))}

  </div>

  <br />

  <button
    onClick={createEquipment}
  >
    Add Equipment
  </button>

  <hr />

</div>


);

}
