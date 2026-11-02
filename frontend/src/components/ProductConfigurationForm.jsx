import { useEffect, useRef, useState } from "react";
import axios from "axios";
import "./FormLayout.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const GENERATED_KEYS = new Set(["id", "row_id", "seq"]);

export default function ProductConfigurationForm({ columns = [], reload, onProductCreated }) {
  const [formData, setFormData] = useState({});
  const [template, setTemplate] = useState({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const edited = useRef(false);

  useEffect(() => {
    let active = true;
    axios.get(`${API}/product_configuration`)
      .then(({ data }) => {
        if (!active) return;
        const first = (Array.isArray(data) ? data : []).find(
          row => Number(row.row_id) === 1 && !row.read_only
        );
        const values = Object.fromEntries(
          Object.entries(first || {}).filter(([name]) => !GENERATED_KEYS.has(name) && !["owner_id", "is_sota", "read_only", "sota_line_type"].includes(name))
        );
        setTemplate(values);
        if (!edited.current) setFormData(values);
      })
      .catch(err => {
        if (active) setError(`Unable to load template: ${err.response?.data?.detail || err.message}`);
      });
    return () => { active = false; };
  }, []);

  const save = async () => {
    if (saving) return;
    setSaving(true);
    setError("");
    try {
      const productCode = String(formData.productcode ?? "").trim();
      if (!productCode) {
        setError("Product Code is required.");
        return;
      }
      const allowed = new Set(columns.map(c => c.column_name));
      const payload = Object.fromEntries(
        Object.entries(formData).filter(([name]) => allowed.has(name) && !GENERATED_KEYS.has(name))
      );
      payload.productcode = productCode;
      const { data } = await axios.post(`${API}/product_configuration`, payload);
      const createdCode = String(data?.productcode ?? productCode).trim();
      edited.current = false;
      setFormData({ ...template });
      await reload?.();
      onProductCreated?.(createdCode);
    } catch (err) {
      setError(`Save failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="form-grid">
        {columns.filter(c => !GENERATED_KEYS.has(c.column_name)).map(column => (
          <div key={column.column_name} className="form-group">
            <label htmlFor={`product_configuration-${column.column_name}`}>
              {column.column_name.replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase())}{column.column_name === "productcode" ? " *" : ""}
            </label>
            <input
              id={`product_configuration-${column.column_name}`}
              value={formData[column.column_name] ?? ""}
              required={column.column_name === "productcode"}
              onChange={event => {
                edited.current = true;
                setFormData(previous => ({ ...previous, [column.column_name]: event.target.value }));
              }}
            />
          </div>
        ))}
      </div>
      {error && <p role="alert">{error}</p>}
      <div className="form-actions">
        <button className="primary-button" onClick={save} disabled={saving || columns.length === 0}>
          {saving ? "Saving…" : "Save Product Configuration"}
        </button>
      </div>
    </div>
  );
}
