import { useEffect, useState } from "react";
import axios from "axios";


const API = import.meta.env.VITE_API_URL;

console.log(API);

export default function EquipmentDatabase() {

    const [columns, setColumns] = useState([]);
    const [equipment, setEquipment] = useState([]);

    const [editingId, setEditingId] = useState(null);
    const [editData, setEditData] = useState({});

  const scrollStyle = { maxHeight: "70vh", overflow: "auto", position: "relative" };
  const tableStyle = { width: "max-content", minWidth: "100%", borderCollapse: "separate", borderSpacing: 0 };
  const stickyHeaderStyle = { position: "sticky", top: 0, zIndex: 3, background: "#173b73", color: "white" };
  const stickyCornerStyle = { ...stickyHeaderStyle, left: 0, zIndex: 5, minWidth: 80, boxShadow: "3px 0 6px -4px rgba(0,0,0,.45)" };
  const stickyFirstCellStyle = { position: "sticky", left: 0, zIndex: 2, background: "#fff", minWidth: 80, boxShadow: "3px 0 6px -4px rgba(0,0,0,.35)" };


    useEffect(() => {
        loadEquipment();
    }, []);



async function loadEquipment() {

    try {

        const res = await axios.get(`${API}/equipment`);

        const rows = Array.isArray(res.data)
            ? res.data
            : [];

        setEquipment(rows);

        if (rows.length > 0) {

            const cols = Object.keys(rows[0])
                .filter(key => key !== "id")
                .map(key => ({
                    column_name: key
                }));

            setColumns(cols);

        } else {

            setColumns([]);

        }

    } catch (err) {

        console.error(err);

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

            <div className="table-wrapper" style={scrollStyle}>

                <table className="equipment-table" style={tableStyle}>

                    <thead>

                        <tr>

                            <th style={stickyCornerStyle}>ID</th>

                            {columns.map(col => (

                                <th style={stickyHeaderStyle} key={col.column_name ?? col.id ?? JSON.stringify(col)}>

                                    {col.column_name}

                                </th>

                            ))}

                            <th style={stickyHeaderStyle}>Actions</th>

                        </tr>

                    </thead>

                    <tbody>

                        {equipment.map(row => (

                            <tr key={row.id}>

                                <td style={stickyFirstCellStyle}>{row.id}</td>

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

                                                disabled={row.read_only}
                                                onClick={()=>

                                                    startEdit(row)

                                                }

                                            >

                                                Edit

                                            </button>

                                            <button

                                                disabled={row.read_only}
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