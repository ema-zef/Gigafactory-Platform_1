import { useEffect, useState } from "react";
import axios from "axios";

export default function EquipmentManager() {

const [equipment, setEquipment] = useState([]);

const [editingId, setEditingId] = useState(null);

const [editData, setEditData] = useState({
technology_name: "",
process: "",
capacity: ""
});

const [newEquipment, setNewEquipment] = useState({
technology_name: "",
process: "",
capacity: ""
});

const API =
import.meta.env.VITE_API_URL ||
"http://localhost:8000";

const loadEquipment = async () => {

```
const response = await axios.get(
  `${API}/equipment`
);

setEquipment(response.data);
```

};

useEffect(() => {
loadEquipment();
}, []);

const createEquipment = async () => {

```
await axios.post(
  `${API}/equipment`,
  newEquipment
);

setNewEquipment({
  technology_name: "",
  process: "",
  capacity: ""
});

loadEquipment();
```

};

const deleteEquipment = async (id) => {

```
await axios.delete(
  `${API}/equipment/${id}`
);

loadEquipment();
```

};

const startEdit = (row) => {

```
setEditingId(row.id);

setEditData({
  technology_name: row.technology_name || "",
  process: row.process || "",
  capacity: row.capacity || ""
});
```

};

const updateEquipment = async (id) => {

```
await axios.put(
  `${API}/equipment/${id}`,
  editData
);

setEditingId(null);

loadEquipment();
```

};

return ( <div>

```
  <h2>Equipment Manager</h2>

  <div
    style={{
      marginBottom: "20px",
      display: "flex",
      gap: "10px"
    }}
  >

    <input
      placeholder="Technology Name"
      value={newEquipment.technology_name}
      onChange={(e) =>
        setNewEquipment({
          ...newEquipment,
          technology_name: e.target.value
        })
      }
    />

    <input
      placeholder="Process"
      value={newEquipment.process}
      onChange={(e) =>
        setNewEquipment({
          ...newEquipment,
          process: e.target.value
        })
      }
    />

    <input
      placeholder="Capacity"
      value={newEquipment.capacity}
      onChange={(e) =>
        setNewEquipment({
          ...newEquipment,
          capacity: e.target.value
        })
      }
    />

    <button onClick={createEquipment}>
      Add Equipment
    </button>

  </div>

  <table border="1" cellPadding="5">

    <thead>
      <tr>
        <th>ID</th>
        <th>Technology</th>
        <th>Process</th>
        <th>Capacity</th>
        <th>Actions</th>
      </tr>
    </thead>

    <tbody>

      {equipment.map((row) => (

        <tr key={row.id}>

          <td>{row.id}</td>

          <td>
            {editingId === row.id ? (
              <input
                value={editData.technology_name}
                onChange={(e) =>
                  setEditData({
                    ...editData,
                    technology_name: e.target.value
                  })
                }
              />
            ) : (
              row.technology_name
            )}
          </td>

          <td>
            {editingId === row.id ? (
              <input
                value={editData.process}
                onChange={(e) =>
                  setEditData({
                    ...editData,
                    process: e.target.value
                  })
                }
              />
            ) : (
              row.process
            )}
          </td>

          <td>
            {editingId === row.id ? (
              <input
                value={editData.capacity}
                onChange={(e) =>
                  setEditData({
                    ...editData,
                    capacity: e.target.value
                  })
                }
              />
            ) : (
              row.capacity
            )}
          </td>

          <td>

            {editingId === row.id ? (
              <>
                <button
                  onClick={() =>
                    updateEquipment(row.id)
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
                    deleteEquipment(row.id)
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
```

);
}
