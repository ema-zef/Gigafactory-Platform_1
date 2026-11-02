import { useState } from 'react';
import axios from 'axios';
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export default function ProductConfigurationTable({ data=[], columns=[], reload }) {
  const [editing, setEditing] = useState(null);
  const [draft, setDraft] = useState({});
  const [error, setError] = useState('');

  const scrollStyle = { maxHeight: "70vh", overflow: "auto", position: "relative" };
  const tableStyle = { width: "max-content", minWidth: "100%", borderCollapse: "separate", borderSpacing: 0 };
  const stickyHeaderStyle = { position: "sticky", top: 0, zIndex: 3, background: "#173b73", color: "white" };
  const stickyCornerStyle = { ...stickyHeaderStyle, left: 0, zIndex: 5, minWidth: 80, boxShadow: "3px 0 6px -4px rgba(0,0,0,.45)" };
  const stickyFirstCellStyle = { position: "sticky", left: 0, zIndex: 2, background: "#fff", minWidth: 80, boxShadow: "3px 0 6px -4px rgba(0,0,0,.35)" };

  const editable = columns.filter(c => !['row_id','owner_id','is_sota','read_only','sota_line_type'].includes(c.column_name));
  async function save(rowId) {
    try { setError(''); await axios.put(`${API}/product_configuration/${rowId}`, draft); setEditing(null); await reload?.(); }
    catch (err) { setError(err.response?.data?.detail || 'Update failed'); }
  }
  async function remove(rowId) {
    if (!window.confirm('Delete this product configuration?')) return;
    try { setError(''); await axios.delete(`${API}/product_configuration/${rowId}`); await reload?.(); }
    catch (err) { setError(err.response?.data?.detail || 'Delete failed'); }
  }
  return <div className="table-wrapper" style={scrollStyle}>{error && <p role="alert">{error}</p>}
    <table style={tableStyle}><thead><tr><th style={stickyCornerStyle}>Row ID</th>{editable.map(c=><th style={stickyHeaderStyle} key={c.column_name}>{c.column_name}</th>)}<th style={stickyHeaderStyle}>Actions</th></tr></thead>
      <tbody>{data.map(row=><tr key={row.row_id}><td style={stickyFirstCellStyle}>{row.row_id}</td>
        {editable.map(c=><td key={c.column_name}>{editing === row.row_id
          ? <input value={draft[c.column_name] ?? ''} onChange={e=>setDraft(prev=>({...prev,[c.column_name]:e.target.value}))}/>
          : String(row[c.column_name] ?? '')}</td>)}
        <td>{row.read_only ? 'SOTA · Read only' : editing === row.row_id ? <>
          <button onClick={()=>save(row.row_id)}>Save</button><button onClick={()=>setEditing(null)}>Cancel</button>
        </> : <><button onClick={()=>{setEditing(row.row_id);setDraft({...row});}}>Edit</button>
          <button onClick={()=>remove(row.row_id)}>Delete</button></>}</td></tr>)}</tbody></table></div>;
}
