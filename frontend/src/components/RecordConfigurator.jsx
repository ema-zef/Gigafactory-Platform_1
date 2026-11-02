import { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./RecordConfigurator.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const SYSTEM = new Set(["id", "row_id", "seq", "owner_id", "is_sota", "read_only", "sota_line_type"]);
const label = key => key.replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());
const numeric = col => /int|numeric|decimal|double|real|float/i.test(String(col.data_type || col.udt_name || ""));
const errorText = e => { const d = e?.response?.data?.detail; return typeof d === "string" ? d : d ? JSON.stringify(d) : e.message || "Request failed"; };
const unit = key => {
  const n = key.toLowerCase();
  if (/%|percent|percentage/.test(n)) return "%";
  if (/eur_per_m2_h/.test(n)) return "€/m²/h";
  if (/eur_per_unit/.test(n)) return "€/unit";
  if (/kgco2e_per/.test(n)) return "kg CO₂e/unit";
  if (/kg_m2/.test(n)) return "kg/m²";
  if (/g_cell/.test(n)) return "g/cell";
  if (/kg_cell/.test(n)) return "kg/cell";
  if (/kwh/.test(n)) return "kWh";
  if (/minutes|_min$/.test(n)) return "min";
  if (/hours|_h$/.test(n)) return "h";
  if (/_m2$/.test(n)) return "m²";
  if (/_kg$/.test(n)) return "kg";
  if (/_m$/.test(n)) return "m";
  return "";
};
const clean = row => Object.fromEntries(Object.entries(row || {}).filter(([k]) => !SYSTEM.has(k)));
const initial = () => ({});

export default function RecordConfigurator({ endpoint, title, subtitle, groups, groupFor, nameFor, idField = "id", initialValues = initial, required = [], lockedFields = [], preferredId = "", onCreated, onSaved }) {
  const [records, setRecords] = useState([]);
  const [columns, setColumns] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [creating, setCreating] = useState(false);
  const [section, setSection] = useState(groups[0].id);
  const [draft, setDraft] = useState({});
  const [baseline, setBaseline] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  
  const load = useCallback(async () => {
    const [r, s] = await Promise.all([axios.get(`${API}/${endpoint}`), axios.get(`${API}/${endpoint}/check`)]);
    const rows = Array.isArray(r.data) ? r.data : [];
    setRecords(rows);
    setColumns((s.data?.columns || []).filter(c => !SYSTEM.has(c.column_name)));
    return rows;
  }, [endpoint]);
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const rows = await load();
        if (!active) return;
        const preferred = preferredId ? rows.find(r => String(r.productcode ?? r.product_code ?? "").trim() === preferredId) : null;
        if (preferredId && !preferred) {
          const values = { ...initialValues(), productcode: preferredId };
          setCreating(true); setDraft(values); setBaseline(values);
        } else {
          const row = preferred || rows.find(r => !r.read_only) || rows[0];
          setSelectedId(row ? recordKey(row, rows.indexOf(row)) : "");
          const values = clean(row); setDraft(values); setBaseline(values);
        }
      } catch (e) { if (active) setError(`Unable to load ${title.toLowerCase()}: ${errorText(e)}`); }
      finally { if (active) setLoading(false); }
    })();
    return () => { active = false; };
  }, [load, title, idField, preferredId]);
  const recordKey = (row, index) => {
    const value = row?.[idField] ?? row?.id ?? row?.row_id;
    return value === undefined || value === null || value === "" ? `index:${index}` : `id:${String(value)}`;
  };
  const selected = records.find((r, i) => recordKey(r, i) === selectedId);
  const readOnly = !creating && Boolean(selected?.read_only || selected?.is_sota);
  const dirty = JSON.stringify(draft) !== JSON.stringify(baseline);
  const grouped = useMemo(() => {
    const out = Object.fromEntries(groups.map(g => [g.id, []]));
    out.other = [];
    columns.forEach(c => { const group = groupFor(c.column_name); (out[group] || out.other).push(c); });
    return out;
  }, [columns, groups, groupFor]);
  const tabs = [...groups, { id: "other", name: "Other parameters", description: "Additional database fields" }, { id: "review", name: "Review", description: "Review all configuration values" }];
  const current = tabs.find(g => g.id === section) || tabs[0];
  const select = id => {
    if (dirty && !window.confirm("Discard unsaved changes and switch records?")) return;
    const row = records.find(r => recordKey(r, records.indexOf(r)) === id);
    const values = clean(row);
    setSelectedId(id); setCreating(false); setDraft(values); setBaseline(values);
    setSection(groups[0].id); setError(""); setNotice("");
  };
  const create = () => {
    if (dirty && !window.confirm("Discard unsaved changes and create a new record?")) return;
    const values = initialValues(records);
    setCreating(true); setSelectedId(""); setDraft(values); setBaseline(values);
    setSection(groups[0].id); setError(""); setNotice("");
  };
  const cancel = () => {
    if (creating) {
      const row = records.find(r => !r.read_only) || records[0];
      const values = clean(row);
      setCreating(false); setSelectedId(row ? recordKey(row, records.indexOf(row)) : ""); setDraft(values); setBaseline(values);
    } else setDraft({ ...baseline });
    setError(""); setNotice("");
  };
  const validate = () => {
    for (const key of required) if (!String(draft[key] ?? "").trim()) return `${label(key)} is required.`;
    for (const c of columns) {
      const v = draft[c.column_name];
      if (v === "" || v == null) continue;
      if (numeric(c) && !Number.isFinite(Number(v))) return `${label(c.column_name)} must be numeric.`;
      if (/%|percent|percentage/.test(c.column_name) && numeric(c) && (Number(v) < 0 || Number(v) > 100)) return `${label(c.column_name)} must be between 0 and 100%.`;
    }
    return "";
  };
  const payloadFor = () => {
    const allowed = new Set(columns.map(c => c.column_name));
    return Object.fromEntries(Object.entries(draft).filter(([k]) => allowed.has(k) && !SYSTEM.has(k)).map(([k, v]) => [k, v === "" ? null : v]));
  };
  const save = async () => {
    if (saving || readOnly) return;
    const issue = validate();
    if (issue) { setError(issue); setSection("review"); return; }
    setSaving(true); setError(""); setNotice("");
    try {
      const payload = payloadFor();
      if (creating) {
        const response = await axios.post(`${API}/${endpoint}`, payload);
        const rows = await load();
        const id = response.data?.[idField];
        const row = rows.find(r => id != null && String(r[idField] ?? r.id ?? r.row_id) === String(id)) ||
          rows.find(r => required.length && required.every(k => String(r[k] ?? "") === String(payload[k] ?? ""))) || rows[rows.length - 1];
        const values = clean(row || payload);
        setCreating(false); setSelectedId(row ? recordKey(row, rows.indexOf(row)) : ""); setDraft(values); setBaseline(values);
        setNotice("Record created successfully.");
        onCreated?.(payload, response.data);
      } else {
        await axios.put(`${API}/${endpoint}/${selected?.[idField] ?? selected?.id ?? selected?.row_id}`, payload);
        const rows = await load();
        const values = clean(rows.find((r, i) => recordKey(r, i) === selectedId) || payload);
        setDraft(values); setBaseline(values); setNotice("Changes saved successfully.");
        onSaved?.(payload);
      }
    } catch (e) { setError(`Save failed: ${errorText(e)}`); }
    finally { setSaving(false); }
  };
  const remove = async () => {
    if (!selected || readOnly || saving) return;
    if (!window.confirm(`Delete "${nameFor(selected)}"? This cannot be undone.`)) return;
    setSaving(true); setError("");
    try {
      await axios.delete(`${API}/${endpoint}/${selected?.[idField] ?? selected?.id ?? selected?.row_id}`);
      const rows = await load();
      const row = rows.find(r => !r.read_only) || rows[0];
      const values = clean(row);
      setSelectedId(row ? recordKey(row, rows.indexOf(row)) : ""); setDraft(values); setBaseline(values);
      setSection(groups[0].id); setNotice("Record deleted.");
    } catch (e) { setError(`Delete failed: ${errorText(e)}`); }
    finally { setSaving(false); }
  };
  const renderField = c => {
    const key = c.column_name;
    const long = /description|notes|comment/i.test(key);
    const disabled = readOnly || saving || (!creating && lockedFields.includes(key));
    return <label className="pc-field" key={key}>
      <span className="pc-field-label">{label(key)} {required.includes(key) && <strong>*</strong>}</span>
      <span className="pc-input-wrap">{long ?
        <textarea rows={3} value={draft[key] ?? ""} disabled={disabled} onChange={e => setDraft(d => ({ ...d, [key]: e.target.value }))} /> :
        <input type={numeric(c) ? "number" : "text"} step={numeric(c) ? "any" : undefined} value={draft[key] ?? ""} disabled={disabled} onChange={e => setDraft(d => ({ ...d, [key]: e.target.value }))} />}
        {unit(key) && <span className="pc-unit">{unit(key)}</span>}</span>
      <span className="pc-field-key">{key}</span>
    </label>;
  };
  const options = records;
  return <div className="pc-page">
    <div className="pc-heading"><div><h2>{title}</h2><p>{subtitle}</p></div>
      <button type="button" className="pc-primary" onClick={create} disabled={loading || saving}>+ New record</button></div>
    <div className="pc-selector"><label htmlFor={`${endpoint}-select`}>Select a record</label>

      <select id={`${endpoint}-select`} value={creating ? "__new__" : selectedId} disabled={loading || saving} onChange={e => select(e.target.value)}>
        {creating && <option value="__new__">New record (unsaved)</option>}
        {!creating && !selectedId && <option value="">Select a record</option>}
        {options.map(r => <option key={recordKey(r, records.indexOf(r))} value={recordKey(r, records.indexOf(r))}>{nameFor(r)}{r.read_only || r.is_sota ? " · Read only" : ""}</option>)}
      </select><div className="pc-status">{readOnly ? <span className="pc-pill">Read only</span> : creating ? <span className="pc-pill">New record</span> : selected ? <span className="pc-pill">Editable</span> : null}{dirty && <span className="pc-unsaved">● Unsaved changes</span>}</div></div>
    {error && <div className="pc-alert" role="alert">{error}</div>}{notice && <div className="pc-notice" role="status">{notice}</div>}
    {loading ? <p>Loading configuration…</p> : !creating && !selected ? <div className="pc-empty">No record selected. Choose “New record” to begin.</div> : <>
      <div className="pc-workspace"><nav className="pc-nav" aria-label={`${title} sections`}>{tabs.filter(t => t.id === "review" || grouped[t.id]?.length).map(t =>
        <button type="button" key={t.id} className={section === t.id ? "pc-nav-active" : ""} onClick={() => setSection(t.id)}><span>{t.name}</span>{t.id !== "review" && <small>{grouped[t.id].length}</small>}</button>)}</nav>
        <main className="pc-panel"><div className="pc-panel-head"><h3>{current.name}</h3><p>{current.description}</p></div>
          {section === "review" ? <div className="pc-review">{tabs.filter(t => t.id !== "review" && grouped[t.id]?.length).map(t => <section key={t.id}><h4>{t.name}</h4><dl>{grouped[t.id].map(c => <div key={c.column_name}><dt>{label(c.column_name)}</dt><dd>{String(draft[c.column_name] ?? "—")} {unit(c.column_name)}</dd></div>)}</dl></section>)}</div>
            : grouped[section]?.length ? <div className="pc-fields">{grouped[section].map(renderField)}</div> : <p className="pc-empty">No fields in this section.</p>}
        </main></div>
      <div className="pc-actions"><div>{readOnly ? "This record cannot be modified." : dirty ? "Unsaved changes" : "All changes saved or unchanged."}</div><div className="pc-action-buttons">
        {!creating && !readOnly && <button type="button" className="pc-danger" disabled={saving} onClick={remove}>Delete</button>}
        {!readOnly && <><button type="button" className="pc-secondary" disabled={saving} onClick={cancel}>Cancel</button><button type="button" className="pc-primary" disabled={saving || !columns.length || (!creating && !dirty)} onClick={save}>{saving ? "Saving…" : creating ? "Create record" : "Save changes"}</button></>}
      </div></div></>}
  </div>;
}
