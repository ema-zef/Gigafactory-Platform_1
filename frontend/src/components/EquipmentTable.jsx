import { useEffect, useState } from "react";
import axios from "axios";

export default function EquipmentTable() {

  const [equipment, setEquipment] = useState([]);

  useEffect(() => {

    axios
      .get("http://localhost:8000/equipment")
      .then((res) => setEquipment(res.data))
      .catch(console.error);

  }, []);

  return (
    <div>

      <h2>Equipment Database</h2>

      <table border="1">

        <thead>
          <tr>
            <th>ID</th>
            <th>Process</th>
            <th>Technology</th>
            <th>Capacity</th>
          </tr>
        </thead>

        <tbody>

          {equipment.map((eq) => (

            <tr key={eq.id}>
              <td>{eq.id}</td>
              <td>{eq.process}</td>
              <td>{eq.technology_name}</td>
              <td>{eq.capacity}</td>
            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}