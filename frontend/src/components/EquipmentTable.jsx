import { useEffect, useState } from "react";
import axios from "axios";


const API = import.meta.env.VITE_API_URL;

console.log(API);

export default function EquipmentDatabase() {

    const [columns, setColumns] = useState([]);
    const [equipment, setEquipment] = useState([]);

    const [editingId, setEditingId] = useState(null);
    const [editData, setEditData] = useState({});

    useEffect(() => {
        loadColumns();
        loadEquipment();
    }, []);

async function loadColumns() {

    try {

        const res = await axios.get(`${API}/equipment/options`);

        console.log("Equipment schema response:", res.data);

        setColumns(Array.isArray(res.data) ? res.data : (res.data.columns ?? []));

    } catch (err) {

        console.error("Equipment schema error:", err);

    }

}

async function loadEquipment() {

    try {

        const res = await axios.get(`${API}/equipment`);

        console.log(res.data[0]);

        setEquipment(res.data ?? []);

    } catch (err) {

        console.error("Equipment data error:", err);

    }

}

    function startEdit(row) {

        setEditingId(row.id);

        setEditData(row);

    }

    async function updateEquipment(id) {

        try {

            await axios.put(

                `${API}/equipment/${id}`,

                editData

            );

            setEditingId(null);

            loadEquipment();

        }

        catch (err) {

            console.error(err);

        }

    }

    async function deleteEquipment(id) {

        if (!window.confirm("Delete this equipment?")) return;

        try {

            await axios.delete(`${API}/equipment/${id}`);

            loadEquipment();

        }

        catch (err) {

            console.error(err);

        }

    }

    return (

        <div className="page-card">

            <h1>Equipment Database</h1>

            <div className="table-wrapper">

                <table className="equipment-table">

                    <thead>

                        <tr>

                            <th>ID</th>

                            {columns.map(col => (

                                <th key={col.column_name ?? col.id ?? JSON.stringify(col)}>

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

                                        {

                                            editingId === row.id

                                            ?

                                            <input

                                                value={

                                                    editData[col.column_name] ?? ""

                                                }

                                                onChange={(e)=>

                                                    setEditData({

                                                        ...editData,

                                                        [col.column_name]:

                                                        e.target.value

                                                    })

                                                }

                                            />

                                            :

                                            String(

                                                row[col.column_name] ?? ""

                                            )

                                        }

                                    </td>

                                ))}

                                <td>

                                    {

                                        editingId === row.id

                                        ?

                                        <>

                                            <button

                                                onClick={()=>

                                                    updateEquipment(row.id)

                                                }

                                            >

                                                Save

                                            </button>

                                            <button

                                                onClick={()=>

                                                    setEditingId(null)

                                                }

                                            >

                                                Cancel

                                            </button>

                                        </>

                                        :

                                        <>

                                            <button

                                                onClick={()=>

                                                    startEdit(row)

                                                }

                                            >

                                                Edit

                                            </button>

                                            <button

                                                onClick={()=>

                                                    deleteEquipment(row.id)

                                                }

                                            >

                                                Delete

                                            </button>

                                        </>

                                    }

                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

        </div>

    );

}