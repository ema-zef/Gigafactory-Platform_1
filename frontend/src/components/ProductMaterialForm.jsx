import { useEffect, useRef, useState } from "react";
import axios from "axios";
import "./FormLayout.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const GENERATED_KEYS = new Set(["id", "row_id", "seq"]);

export default function ProductMaterialForm({ columns = [], reload, productCode = "", onMaterialSaved }) {
  const [formData, setFormData] = useState({});
  const [template, setTemplate] = useState({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const edited = useRef(false);

  useEffect(() => {
    let active = true;
    axios.get(`${API}/product_material`)
      .then(({ data }) => {
        if (!active) return;
        const first = (Array.isArray(data) ? data : []).find(
          row => Number(row.seq) === 1 && !row.read_only
        );
        const values = Object.fromEntries(
          Object.entries(first || {}).filter(([name]) => !GENERATED_KEYS.has(name) && !["owner_id", "is_sota", "read_only", "sota_line_type"].includes(name))
        );
        if (productCode) values.productcode = productCode;
        setTemplate(values);
        if (!edited.current) setFormData(values);
      })
      .catch(err => {
        if (active) setError(`Unable to load template: ${err.response?.data?.detail || err.message}`);
      });
    return () => { active = false; };
  }, [productCode]);

  const save = async () => {
    if (saving) return;
    setSaving(true);
    setError("");
    try {
      const requiredProductCode = String(productCode || formData.productcode || "").trim();
      if (!requiredProductCode) {
        setError("Product Code is required.");
        return;
      }
      const allowed = new Set(columns.map(c => c.column_name));
      const payload = Object.fromEntries(
        Object.entries(formData).filter(([name]) => allowed.has(name) && !GENERATED_KEYS.has(name))
      );
      payload.productcode = requiredProductCode;
      await axios.post(`${API}/product_material`, payload);
      edited.current = false;
      setFormData({ ...template, ...(productCode ? { productcode: productCode } : {}) });
      await reload?.();
      onMaterialSaved?.(requiredProductCode);
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
            <label htmlFor={`product_material-${column.column_name}`}>
              {column.column_name.replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase())}{column.column_name === "productcode" ? " *" : ""}
            </label>
            <input
              id={`product_material-${column.column_name}`}
              value={column.column_name === "productcode" && productCode ? productCode : (formData[column.column_name] ?? "")}
              required={column.column_name === "productcode"}
              readOnly={column.column_name === "productcode" && Boolean(productCode)}
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
          {saving ? "Saving…" : "Save Product Material"}
        </button>
      </div>
    </div>
  );
}
