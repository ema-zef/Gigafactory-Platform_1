import { useEffect, useState } from "react";
import axios from "axios";

export default function EquipmentPalette() {

  const [equipment, setEquipment] =
    useState([]);

  const API =
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000";

  useEffect(() => {

    axios
      .get(`${API}/equipment`)
      .then((res) =>
        setEquipment(res.data)
      );

  }, []);

  return (
    <div
      style={{
        width: "250px",
        borderRight: "1px solid #ccc",
        padding: "10px",
        overflowY: "auto",
      }}
    >
      <h3>Equipment Palette</h3>

      {equipment.map((item) => (

        <div
          key={item.id}
          draggable
          onDragStart={(e) =>
            e.dataTransfer.setData(
              "equipment",
              JSON.stringify(item)
            )
          }
          style={{
            padding: "8px",
            marginBottom: "8px",
            border: "1px solid #999",
            borderRadius: "4px",
            cursor: "grab",
            background: "#f8f8f8",
          }}
        >
          {item.technology_name}
        </div>

      ))}
    </div>
  );
}