import { useState } from "react";
import "./FormLayout.css";

export default function EquipmentForm({ columns = [], equipment = [], newEquipment, setNewEquipment, createEquipment }) {
  const [error, setError] = useState("");
  const processes = [...new Set(equipment.map(row => row.process).filter(value => value != null && String(value).trim() !== ""))];

  const changeField = (name, value) => {
    if (name !== "process") {
      setNewEquipment(previous => ({ ...previous, [name]: value }));
      return;
    }
    const match = equipment
      .filter(row => String(row.process ?? "").trim().toLowerCase() === String(value).trim().toLowerCase())
      .sort((a, b) => Number(a.id) - Number(b.id))[0];
    const allowed = new Set(columns.map(c => c.column_name));
    const values = match
      ? Object.fromEntries(Object.entries(match).filter(([key]) => allowed.has(key) && key !== "id" && key !== "process"))
      : {};
    // A new process clears values from the previously selected process.
    setNewEquipment({ ...values, process: value });
  };

  const save = async () => {
    setError("");
    try { await createEquipment(); }
    catch (err) { setError(`Save failed: ${err.response?.data?.detail || err.message}`); }
  };

  return (
    <div>
      <datalist id="equipment-process-options">
        {processes.map(process => <option key={String(process)} value={String(process)} />)}
      </datalist>
      <div className="form-grid">
        {columns.filter(c => c.column_name !== "id").map(column => (
          <div key={column.column_name} className="form-group">
            <label htmlFor={`equipment-${column.column_name}`}>
              {column.column_name.replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase())}
            </label>
            <input
              id={`equipment-${column.column_name}`}
              list={column.column_name === "process" ? "equipment-process-options" : undefined}
              value={newEquipment[column.column_name] ?? ""}
              onChange={event => changeField(column.column_name, event.target.value)}
            />
          </div>
        ))}
      </div>
      {error && <p role="alert">{error}</p>}
      <div className="form-actions">
        <button className="primary-button" onClick={save}>Save Equipment</button>
      </div>
    </div>
  );
}
