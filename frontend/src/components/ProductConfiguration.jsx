import { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./ProductConfigurator.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const HIDDEN = new Set(["id", "row_id", "seq", "owner_id", "is_sota", "read_only", "sota_line_type"]);
const NO_SEND = new Set(["id", "row_id", "seq", "owner_id", "is_sota", "read_only", "sota_line_type"]);
const GROUPS = [
  { id: "general", name: "General & Cell", description: "Product identity, cell capacity and shared geometry" },
  { id: "cathode", name: "Cathode", description: "Cathode geometry, formulation and current collector" },
  { id: "anode", name: "Anode", description: "Anode geometry, formulation and current collector" },
  { id: "assembly", name: "Cell Assembly", description: "Separator, electrolyte, housing and sealing" },
  { id: "other", name: "Other Parameters", description: "Additional fields from your database" },
  { id: "review", name: "Review", description: "Inspect the complete product before saving" },
];
const prettify = (name) => name.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())
  .replace(/\bAm\b/g, "Active material").replace(/\bColl\b/g, "Collector")
  .replace(/\bElectrolite\b/g, "Electrolyte").replace(/\bMin\b/g, "Minimum");
function sectionFor(name) {
  const n = name.toLowerCase();
  if (n.startsWith("cathode_") || n.startsWith("cath_") || n.includes("cathode")) return "cathode";
  if (n.startsWith("anode_") || n.includes("anode")) return "anode";
  if (/separator|electrolite|electrolyte|housing|sealing/.test(n)) return "assembly";
  if (/product|cell_|number_of_electrodes|effective_parent_web|chemistry|form_factor/.test(n)) return "general";
  return "other";
}
function unitFor(name) {
  const n = name.toLowerCase();
  if (n.includes("w%") || n.endsWith("_percent") || n.endsWith("_percentage")) return "%";
  if (n.includes("kg_m2")) return "kg/m²";
  if (n.includes("g_cell")) return "g/cell";
  if (n.includes("kg_cell")) return "kg/cell";
  if (n.endsWith("_kwh")) return "kWh";
  if (n.endsWith("_m2")) return "m²";
  if (n.endsWith("_m")) return "m";
  return "";
}
function isNumeric(column) {
  return /int|numeric|decimal|double|real|float|serial/i.test(String(column.data_type || column.udt_name || ""));
}
function normalize(row) { return Object.fromEntries(Object.entries(row || {}).filter(([k]) => !NO_SEND.has(k))); }
function errorMessage(error) {
  const detail = error?.response?.data?.detail;
  return typeof detail === "string" ? detail : detail ? JSON.stringify(detail) : error?.message || "Request failed";
}

export default function ProductConfigurationManager() {
  const navigate = useNavigate();
  const [records, setRecords] = useState([]);
  const [columns, setColumns] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [creating, setCreating] = useState(false);
  const [section, setSection] = useState("general");
  const [draft, setDraft] = useState({});
  const [baseline, setBaseline] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadData = useCallback(async () => {
    const [dataResponse, schemaResponse] = await Promise.all([
      axios.get(`${API}/product_configuration`),
      axios.get(`${API}/product_configuration/check`),
    ]);
    const rows = Array.isArray(dataResponse.data) ? dataResponse.data : [];
    setRecords(rows);
    setColumns((schemaResponse.data?.columns || []).filter(c => !HIDDEN.has(c.column_name)));
    return rows;
  }, []);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const rows = await loadData();
        if (!active) return;
        const first = rows.find(r => !r.read_only) || rows[0];
        if (first) {
          setSelectedId(String(first.row_id));
          const values = normalize(first);
          setDraft(values);
          setBaseline(values);
        }
      } catch (e) { if (active) setError(`Unable to load products: ${errorMessage(e)}`); }
      finally { if (active) setLoading(false); }
    })();
    return () => { active = false; };
  }, [loadData]);

  const selected = records.find(r => String(r.row_id) === selectedId);
  const readOnly = !creating && !!selected?.read_only;
  const dirty = JSON.stringify(draft) !== JSON.stringify(baseline);
  const grouped = useMemo(() => {
    const groups = Object.fromEntries(GROUPS.map(g => [g.id, []]));
    for (const column of columns) groups[sectionFor(column.column_name)].push(column);
    return groups;
  }, [columns]);
  const changeSelection = (nextId) => {
    if (dirty && !window.confirm("Discard unsaved changes and switch products?")) return;
    const row = records.find(r => String(r.row_id) === nextId);
    setCreating(false);
    setSelectedId(nextId);
    const values = normalize(row);
    setDraft(values);
    setBaseline(values);
    setSection("general");
    setError(""); setNotice("");
  };
  const createNew = () => {
    if (dirty && !window.confirm("Discard unsaved changes and create a new product?")) return;
    // Match the previous add form: row_id 1 is the optional editable template.
    const template = records.find(r => Number(r.row_id) === 1 && !r.read_only);
    const values = { ...normalize(template), productcode: "" };
    setCreating(true); setSelectedId(""); setDraft(values); setBaseline(values);
    setSection("general"); setError(""); setNotice("");
  };
  const cancel = () => {
    if (creating) {
      const first = records.find(r => !r.read_only) || records[0];
      const values = normalize(first);
      setCreating(false); setSelectedId(first ? String(first.row_id) : "");
      setDraft(values); setBaseline(values);
    } else setDraft({ ...baseline });
    setError(""); setNotice("");
  };
  const validate = () => {
    if (!String(draft.productcode ?? "").trim()) return "Product Code is required.";
    for (const column of columns) {
      const key = column.column_name;
      const value = draft[key];
      if (value === "" || value == null) continue;
      if (isNumeric(column) && !Number.isFinite(Number(value))) return `${prettify(key)} must be numeric.`;
      if (key.includes("w%") && (Number(value) < 0 || Number(value) > 100)) return `${prettify(key)} must be between 0 and 100%.`;
    }
    for (const side of ["cathode", "anode"]) {
      const coated = Number(draft[`${side}_coated_width_m`] ?? draft[`${side}_width_m`]);
      const collector = Number(draft[`${side}_coll_width_m`]);
      if (coated > 0 && collector > 0 && coated > collector) return `${prettify(side)} coated width cannot exceed collector width.`;
    }
    return "";
  };
  const save = async () => {
    if (saving || readOnly) return;
    const issue = validate();
    if (issue) { setError(issue); setSection("review"); return; }
    setSaving(true); setError(""); setNotice("");
    try {
      const allowed = new Set(columns.map(c => c.column_name));
      const payload = Object.fromEntries(Object.entries(draft).filter(([key]) => allowed.has(key) && !NO_SEND.has(key)));
      payload.productcode = String(payload.productcode).trim();
      if (creating) {
        const { data } = await axios.post(`${API}/product_configuration`, payload);
        const code = String(data?.productcode ?? payload.productcode).trim();
        await loadData();
        setCreating(false); setDraft({ ...payload }); setBaseline({ ...payload });
        setNotice("Product created successfully.");
        navigate("/materials", { state: { productCode: code, requireMaterial: true } });
      } else {
        await axios.put(`${API}/product_configuration/${selectedId}`, payload);
        const rows = await loadData();
        const updated = rows.find(r => String(r.row_id) === selectedId);
        const values = normalize(updated || payload);
        setDraft(values); setBaseline(values);
        setNotice("Product saved successfully.");
      }
    } catch (e) { setError(`Save failed: ${errorMessage(e)}`); }
    finally { setSaving(false); }
  };
  const remove = async () => {
    if (!selected || readOnly || saving) return;
    if (!window.confirm(`Delete product "${selected.productcode || selectedId}"? This cannot be undone.`)) return;
    setSaving(true); setError("");
    try {
      await axios.delete(`${API}/product_configuration/${selectedId}`);
      const rows = await loadData();
      const first = rows.find(r => !r.read_only) || rows[0];
      const values = normalize(first);
      setSelectedId(first ? String(first.row_id) : "");
      setDraft(values); setBaseline(values);
      setSection("general"); setNotice("Product deleted.");
    } catch (e) { setError(`Delete failed: ${errorMessage(e)}`); }
    finally { setSaving(false); }
  };
  const renderField = (column) => {
    const key = column.column_name;
    const unit = unitFor(key);
    const value = draft[key] ?? "";
    const isLong = /description|notes|comment/i.test(key);
    return <label className="pc-field" key={key}>
      <span className="pc-field-label">{prettify(key)} {key === "productcode" && <strong>*</strong>}</span>
      <span className="pc-input-wrap">
        {isLong ? <textarea rows={3} value={value} disabled={readOnly || saving} onChange={e => setDraft(d => ({ ...d, [key]: e.target.value }))} />
          : <input type={isNumeric(column) ? "number" : "text"} step={isNumeric(column) ? "any" : undefined}
            value={value} disabled={readOnly || saving} onChange={e => setDraft(d => ({ ...d, [key]: e.target.value }))} />}
        {unit && <span className="pc-unit">{unit}</span>}
      </span>
      <span className="pc-field-key">{key}</span>
    </label>;
  };
  const currentGroup = GROUPS.find(g => g.id === section);

  return <div className="pc-page">
    <div className="pc-heading"><div><h2>Product Configurator</h2><p>Configure cell geometry, electrode materials and assembly parameters.</p></div>
      <button className="pc-primary" type="button" onClick={createNew} disabled={loading || saving}>+ New product</button></div>
    <div className="pc-selector"><label htmlFor="pc-product">Selected product</label>
      <select id="pc-product" value={creating ? "__new__" : selectedId} disabled={loading || saving} onChange={e => changeSelection(e.target.value)}>
        {creating && <option value="__new__">New product (unsaved)</option>}
        {!creating && !selectedId && <option value="">Select a product</option>}
        {records.map(row => <option key={row.row_id} value={String(row.row_id)}>{row.productcode || `Product ${row.row_id}`}{row.read_only ? " · SOTA (read only)" : ""}</option>)}
      </select>
      <div className="pc-status">{readOnly ? <span className="pc-pill">SOTA · Read only</span> : creating ? <span className="pc-pill">New product</span> : selected ? <span className="pc-pill">Editable</span> : null}
        {dirty && <span className="pc-unsaved">● Unsaved changes</span>}</div>
    </div>
    {error && <div className="pc-alert" role="alert">{error}</div>}
    {notice && <div className="pc-notice" role="status">{notice}</div>}
    {loading ? <p>Loading product configuration…</p> : !creating && !selected ? <div className="pc-empty">No product selected. Choose “New product” to create one.</div> : <>
      <div className="pc-workspace"><nav className="pc-nav" aria-label="Product configuration sections">
        {GROUPS.filter(g => g.id === "review" || g.id !== "other" || grouped.other.length > 0).map(g =>
          <button type="button" key={g.id} className={section === g.id ? "pc-nav-active" : ""} onClick={() => setSection(g.id)}>
            <span>{g.name}</span>{g.id !== "review" && <small>{grouped[g.id].length}</small>}
          </button>)}
      </nav><main className="pc-panel"><div className="pc-panel-head"><h3>{currentGroup.name}</h3><p>{currentGroup.description}</p></div>
        {section === "review" ? <div className="pc-review">{GROUPS.filter(g => g.id !== "review" && grouped[g.id].length).map(g => <section key={g.id}>
          <h4>{g.name}</h4><dl>{grouped[g.id].map(c => <div key={c.column_name}><dt>{prettify(c.column_name)}</dt><dd>{String(draft[c.column_name] ?? "—")} {unitFor(c.column_name)}</dd></div>)}</dl>
        </section>)}</div> : grouped[section].length ? <div className="pc-fields">{grouped[section].map(renderField)}</div>
          : <p className="pc-empty">No fields in this section.</p>}
      </main></div>
      <div className="pc-actions"><div>{readOnly ? "This SOTA product cannot be modified." : dirty ? "You have changes that are not saved." : "All changes saved or unchanged."}</div>
        <div className="pc-action-buttons">{!creating && !readOnly && <button type="button" className="pc-danger" onClick={remove} disabled={saving}>Delete product</button>}
          {!readOnly && <><button type="button" className="pc-secondary" onClick={cancel} disabled={saving}>Cancel</button>
          <button type="button" className="pc-primary" onClick={save} disabled={saving || columns.length === 0 || (!creating && !dirty)}>{saving ? "Saving…" : creating ? "Create product" : "Save changes"}</button></>}</div>
      </div></>}
  </div>;
}
