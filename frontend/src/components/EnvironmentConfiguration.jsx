import { useEffect, useMemo, useState } from "react";
import axios from "axios";

const ENVIRONMENT_TYPES = [
  { value: "dry_room", label: "Dry Room" },
  { value: "glove_box", label: "Glove Box" },
  { value: "mini_environment", label: "Mini Environment" },
];

const HIDDEN_FIELDS = new Set([
  "id",
  "owner_id",
  "created_at",
  "updated_at",
  "is_sota",
  "read_only",
  "sota_line_type",
]);

const LABELS = {
  code: "Code",
  name: "Name",
  environment_type: "Environment Type",
  area_factor: "Area Factor",
  fixed_area_m2: "Fixed Area (m²)",
  design_area_m2: "Design / Capacity Area (m²)",
  purchase_installation_cost_eur: "Purchase + Installation CAPEX (€)",
  electricity_kwh_per_m2_h: "Electricity (kWh/m²/h)",
  gas_kwh_per_m2_h: "Gas / Thermal Energy (kWh/m²/h)",
  fixed_electricity_kwh_day: "Fixed Electricity (kWh/day)",
  fixed_gas_kwh_day: "Fixed Gas / Thermal Energy (kWh/day)",
  operator_count: "Environment Operators",
  maintenance_cost_eur_day: "Maintenance Cost (€/day)",
  is_configured: "Configured / Active",
  notes: "Notes",
};

const NUMERIC_FIELDS = new Set([
  "area_factor",
  "fixed_area_m2",
  "design_area_m2",
  "purchase_installation_cost_eur",
  "electricity_kwh_per_m2_h",
  "gas_kwh_per_m2_h",
  "fixed_electricity_kwh_day",
  "fixed_gas_kwh_day",
  "operator_count",
  "maintenance_cost_eur_day",
]);

const EMPTY_FORM = {
  code: "",
  name: "",
  environment_type: "dry_room",
  area_factor: "1",
  fixed_area_m2: "0",
  design_area_m2: "",
  purchase_installation_cost_eur: "",
  electricity_kwh_per_m2_h: "0",
  gas_kwh_per_m2_h: "0",
  fixed_electricity_kwh_day: "0",
  fixed_gas_kwh_day: "0",
  operator_count: "0",
  maintenance_cost_eur_day: "0",
  is_configured: false,
  notes: "",
};

function labelFor(field) {
  return LABELS[field] || field.replaceAll("_", " ");
}

function normalizePayload(form, editableFields) {
  const payload = {};
  editableFields.forEach((field) => {
    if (!(field in form)) return;
    if (NUMERIC_FIELDS.has(field)) {
      payload[field] = form[field] === "" ? null : Number(form[field]);
    } else {
      payload[field] = form[field];
    }
  });
  return payload;
}

export default function EnvironmentConfiguration() {
  const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const [records, setRecords] = useState([]);
  const [columns, setColumns] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [showTable, setShowTable] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const editableFields = useMemo(
    () =>
      columns
        .map((column) => column.column_name)
        .filter((name) => !HIDDEN_FIELDS.has(name)),
    [columns]
  );

  async function loadData() {
    try {
      setError("");
      const [dataResponse, schemaResponse] = await Promise.all([
        axios.get(`${API}/environment_configuration`),
        axios.get(`${API}/environment_configuration/check`),
      ]);
      setRecords(dataResponse.data || []);
      setColumns(schemaResponse.data.columns || []);
    } catch (err) {
      console.error("Environment Configuration load error:", err);
      setError(err.response?.data?.detail || "Unable to load environment configuration.");
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  function startAdd() {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setShowForm(true);
  }

  function startEdit(record) {
    if (record.read_only) return;
    const next = { ...EMPTY_FORM };
    Object.keys(next).forEach((key) => {
      if (record[key] !== null && record[key] !== undefined) {
        next[key] = record[key];
      }
    });
    next.is_configured = Boolean(record.is_configured);
    setEditingId(record.id);
    setForm(next);
    setShowForm(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setShowForm(false);
    setError("");
  }

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function save(event) {
    event.preventDefault();

    if (!form.code.trim() || !form.name.trim() || !form.environment_type) {
      setError("Code, Name and Environment Type are required.");
      return;
    }

    if (form.is_configured) {
      const invalid = [...NUMERIC_FIELDS].some(
        (field) => form[field] === "" || Number.isNaN(Number(form[field])) || Number(form[field]) < 0
      );
      if (invalid) {
        setError("All engineering parameters must be valid non-negative numbers before activation.");
        return;
      }
    }

    setBusy(true);
    setError("");

    try {
      const payload = normalizePayload(form, editableFields);

      if (editingId) {
        await axios.put(`${API}/environment_configuration/${editingId}`, payload);
      } else {
        await axios.post(`${API}/environment_configuration`, payload);
      }

      await loadData();
      cancelEdit();
    } catch (err) {
      console.error("Environment Configuration save error:", err);
      setError(err.response?.data?.detail || "Unable to save environment configuration.");
    } finally {
      setBusy(false);
    }
  }

  async function remove(record) {
    if (record.read_only) return;
    if (!window.confirm(`Delete ${record.name || record.code}?`)) return;

    try {
      setError("");
      await axios.delete(`${API}/environment_configuration/${record.id}`);
      await loadData();
    } catch (err) {
      console.error("Environment Configuration delete error:", err);
      setError(err.response?.data?.detail || "Unable to delete environment configuration.");
    }
  }

  function renderField(field) {
    if (field === "environment_type") {
      return (
        <select
          value={form.environment_type}
          onChange={(e) => updateField(field, e.target.value)}
          required
        >
          {ENVIRONMENT_TYPES.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );
    }

    if (field === "is_configured") {
      return (
        <label style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <input
            type="checkbox"
            checked={Boolean(form.is_configured)}
            onChange={(e) => updateField(field, e.target.checked)}
          />
          {form.is_configured ? "Active" : "Not configured"}
        </label>
      );
    }

    if (field === "notes") {
      return (
        <textarea
          rows={3}
          value={form.notes ?? ""}
          onChange={(e) => updateField(field, e.target.value)}
        />
      );
    }

    return (
      <input
        type={NUMERIC_FIELDS.has(field) ? "number" : "text"}
        step={NUMERIC_FIELDS.has(field) ? "any" : undefined}
        min={NUMERIC_FIELDS.has(field) ? "0" : undefined}
        value={form[field] ?? ""}
        onChange={(e) => updateField(field, e.target.value)}
        required={field === "code" || field === "name"}
      />
    );
  }

  return (
    <div>
      <h2 style={{ textAlign: "center", color: "#173b73", marginBottom: 25 }}>
        Environment Configuration
      </h2>

      <p style={{ maxWidth: 900 }}>
        Configure the shared infrastructure used by route steps assigned to a Dry Room,
        Glove Box or Mini Environment. Keep a record inactive until its engineering
        assumptions have been validated.
      </p>

      {error && (
        <div style={{ margin: "12px 0", padding: 10, border: "1px solid #b33" }}>
          {error}
        </div>
      )}

      <button onClick={showForm ? cancelEdit : startAdd}>
        {showForm ? "▼ Hide Form" : "► Add Environment Configuration"}
      </button>

      {showForm && (
        <div className="form-card" style={{ marginTop: 16 }}>
          <div className="form-title">
            {editingId ? "Edit Environment Configuration" : "Add Environment Configuration"}
          </div>

          <form onSubmit={save}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                gap: 14,
                marginTop: 14,
              }}
            >
              {editableFields.map((field) => (
                <label key={field} style={{ display: "grid", gap: 6 }}>
                  <span>{labelFor(field)}</span>
                  {renderField(field)}
                </label>
              ))}
            </div>

            <div style={{ display: "flex", gap: 10, marginTop: 18 }}>
              <button type="submit" disabled={busy}>
                {busy ? "Saving..." : editingId ? "Update" : "Create"}
              </button>
              <button type="button" onClick={cancelEdit} disabled={busy}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <br />
      <br />

      <button onClick={() => setShowTable((value) => !value)}>
        {showTable ? "▼ Hide Table" : "► View Environment Configurations"}
      </button>

      {showTable && (
        <div style={{ overflowX: "auto", marginTop: 16 }}>
          <table style={{ borderCollapse: "collapse", minWidth: 1500, width: "100%" }}>
            <thead>
              <tr>
                <th>Code</th>
                <th>Name</th>
                <th>Environment</th>
                <th>Area Factor</th>
                <th>Fixed Area m²</th>
                <th>Electricity kWh/m²/h</th>
                <th>Gas kWh/m²/h</th>
                <th>Fixed Electricity kWh/day</th>
                <th>Fixed Gas kWh/day</th>
                <th>Operators</th>
                <th>Maintenance €/day</th>
                <th>Configured</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={`${record.is_sota ? "sota" : "private"}-${record.id}`}>
                  <td>{record.code}</td>
                  <td>{record.name}</td>
                  <td>{labelFor(record.environment_type)}</td>
                  <td>{record.area_factor}</td>
                  <td>{record.fixed_area_m2}</td>
                  <td>{record.electricity_kwh_per_m2_h}</td>
                  <td>{record.gas_kwh_per_m2_h}</td>
                  <td>{record.fixed_electricity_kwh_day}</td>
                  <td>{record.fixed_gas_kwh_day}</td>
                  <td>{record.operator_count}</td>
                  <td>{record.maintenance_cost_eur_day}</td>
                  <td>{record.is_configured ? "Yes" : "No"}</td>
                  <td>
                    {record.read_only ? (
                      "Read only"
                    ) : (
                      <div style={{ display: "flex", gap: 8 }}>
                        <button onClick={() => startEdit(record)}>Edit</button>
                        <button onClick={() => remove(record)}>Delete</button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
              {!records.length && (
                <tr>
                  <td colSpan="13">No environment configurations found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
