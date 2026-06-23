import { useEffect, useState } from "react";
import axios from "axios";

import EquipmentForm from "./EquipmentForm";
import EquipmentTable from "./EquipmentTable";
import EquipmentFilters from "./EquipmentFilters";

export default function EquipmentManager() {

const API =
import.meta.env.VITE_API_URL ||
"http://localhost:8000";

const [equipment, setEquipment] = useState([]);
const [columns, setColumns] = useState([]);

const [editData, setEditData] = useState({});
const [editingId, setEditingId] = useState(null);

const [newEquipment, setNewEquipment] = useState({});

useEffect(() => {
loadData();
}, []);

const loadData = async () => {


const equipmentResponse =
  await axios.get(
    `${API}/equipment`
  );

const schemaResponse =
  await axios.get(
    `${API}/equipment/check`
  );

setEquipment(
  equipmentResponse.data
);

setColumns(
  schemaResponse.data.columns
    .filter(c => c.column_name !== "id")
);


};

const createEquipment = async () => {


await axios.post(
  `${API}/equipment`,
  newEquipment
);

setNewEquipment({});

loadData();


};

const deleteEquipment = async (id) => {


await axios.delete(
  `${API}/equipment/${id}`
);

loadData();


};

const startEdit = (row) => {


setEditingId(row.id);

setEditData({ ...row });


};

const updateEquipment = async (id) => {


await axios.put(
  `${API}/equipment/${id}`,
  editData
);

setEditingId(null);

loadData();


};

return (


<div>

  <h2>Equipment Manager</h2>

  <EquipmentFilters
    columns={columns}
  />

  <EquipmentForm
    columns={columns}
    newEquipment={newEquipment}
    setNewEquipment={setNewEquipment}
    createEquipment={createEquipment}
  />

  <EquipmentTable
    columns={columns}
    equipment={equipment}
    editingId={editingId}
    editData={editData}
    setEditData={setEditData}
    startEdit={startEdit}
    updateEquipment={updateEquipment}
    deleteEquipment={deleteEquipment}
    setEditingId={setEditingId}
  />

</div>


);

}
