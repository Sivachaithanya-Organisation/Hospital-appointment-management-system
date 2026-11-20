import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { api } from "../api";
import { Alert, Chip, DAYS, Empty, Field, fmtDate, hm } from "../ui";

export function AdminShell() {
  const tabs = [["/admin", "Overview", true], ["/admin/appointments", "Appointments"], ["/admin/patients", "Patients"], ["/admin/doctors", "Doctors"], ["/admin/departments", "Departments"]];
  return (
    <>
      <div className="subnav">{tabs.map(([to, label, end]) => <NavLink key={to} to={to} end={end}>{label}</NavLink>)}</div>
      <Outlet />
    </>
  );
}

export function Overview() {
  const [s, setS] = useState(null);
  useEffect(() => { api.get("/admin/stats").then(setS); }, []);
  if (!s) return null;
  const items = [["Appointments today", s.today], ["Booked", s.by_status.booked || 0], ["Completed", s.by_status.completed || 0], ["Cancelled", s.by_status.cancelled || 0], ["Patients", s.patients], ["Doctors", s.doctors], ["Departments", s.departments]];
  return (
    <>
      <h2>Overview</h2>
      <div className="stats">{items.map(([k, v]) => <div key={k}><b>{v}</b><span>{k}</span></div>)}</div>
    </>
  );
}

export function AdminAppointments() {
  const [rows, setRows] = useState(null);
  const [status, setStatus] = useState("");
  const [date, setDate] = useState("");
  const [err, setErr] = useState("");
  const load = () => {
    const qs = new URLSearchParams();
    if (status) qs.set("status", status);
    if (date) qs.set("date", date);
    api.get(`/admin/appointments?${qs}`).then(setRows).catch((e) => setErr(e.message));
  };
  useEffect(load, [status, date]);
  const mark = async (id, st) => {
    try { await api.patch(`/admin/appointments/${id}`, { status: st }); load(); } catch (e) { setErr(e.message); }
  };
  return (
    <>
      <div className="head"><h2>Appointments</h2>
        <div className="row">
          <select value={status} onChange={(e) => setStatus(e.target.value)}><option value="">All statuses</option><option>booked</option><option>completed</option><option>cancelled</option></select>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>
      </div>
      <Alert error={err} />
      {rows && !rows.length && <Empty>No appointments match these filters.</Empty>}
      {!!rows?.length && (
        <div className="scroll"><table>
          <thead><tr><th>When</th><th>Patient</th><th>Doctor</th><th>Department</th><th>Status</th><th></th></tr></thead>
          <tbody>{rows.map((a) => (
            <tr key={a.id}>
              <td>{fmtDate(a.appointment_date)}<br /><b>{hm(a.slot_time)}</b></td>
              <td>{a.patient_name}</td><td>{a.doctor_name}</td><td>{a.department_name}</td>
              <td><Chip status={a.status} /></td>
              <td className="actions">
                {a.status === "booked" && <><button className="btn small" onClick={() => mark(a.id, "completed")}>Complete</button><button className="btn small ghost" onClick={() => mark(a.id, "cancelled")}>Cancel</button></>}
              </td>
            </tr>))}
          </tbody>
        </table></div>
      )}
    </>
  );
}

export function AdminPatients() {
  const [q, setQ] = useState("");
  const [list, setList] = useState([]);
  const [sel, setSel] = useState(null);
  const [detail, setDetail] = useState(null);
  const blank = { diagnosis: "", prescription: "", notes: "" };
  const [rec, setRec] = useState(blank);
  const [msg, setMsg] = useState({});
  useEffect(() => {
    const t = setTimeout(() => api.get(`/admin/patients?q=${encodeURIComponent(q)}`).then(setList), 250);
    return () => clearTimeout(t);
  }, [q]);
  const open = async (id) => { setSel(id); setDetail(await api.get(`/admin/patients/${id}`)); };
  const addRecord = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/admin/patients/${sel}/records`, { diagnosis: rec.diagnosis, prescription: rec.prescription || null, notes: rec.notes || null });
      setRec(blank); setMsg({ ok: "Record added" }); open(sel);
    } catch (x) { setMsg({ error: x.message }); }
  };
  const p = detail?.patient;
  return (
    <>
      <h2>Patients</h2>
      <div className="split">
        <div>
          <input placeholder="Search name, email or phone" value={q} onChange={(e) => setQ(e.target.value)} />
          <div className="stack tight">
            {list.map((x) => (
              <button key={x.id} className={`pick ${sel === x.id ? "on" : ""}`} onClick={() => open(x.id)}>
                <b>{x.full_name}</b><span>{x.email}</span>
              </button>
            ))}
            {!list.length && <Empty>No patients found.</Empty>}
          </div>
        </div>
        <div>
          {!p && <Empty>Select a patient to see their records and visits.</Empty>}
          {p && (
            <>
              <div className="panel">
                <h3>{p.full_name}</h3>
                <p className="muted">{[p.email, p.phone, p.gender, p.blood_group && `Blood group ${p.blood_group}`, p.dob && `Born ${p.dob}`].filter(Boolean).join(" · ")}</p>
                {p.address && <p className="muted">{p.address}</p>}
              </div>
              <form className="panel" onSubmit={addRecord}>
                <h3>Add medical record</h3>
                <Alert {...msg} />
                <Field label="Diagnosis"><input required minLength={2} value={rec.diagnosis} onChange={(e) => setRec({ ...rec, diagnosis: e.target.value })} /></Field>
                <Field label="Prescription"><textarea rows={2} value={rec.prescription} onChange={(e) => setRec({ ...rec, prescription: e.target.value })} /></Field>
                <Field label="Notes"><textarea rows={2} value={rec.notes} onChange={(e) => setRec({ ...rec, notes: e.target.value })} /></Field>
                <button className="btn">Save record</button>
              </form>
              <h3>History</h3>
              <div className="stack">
                {detail.records.map((r) => (
                  <div className="record" key={r.id}>
                    <div className="muted">{new Date(r.created_at).toLocaleDateString()}{r.doctor_name && ` · ${r.doctor_name}`}</div>
                    <p><b>{r.diagnosis}</b></p>
                    {r.prescription && <p>{r.prescription}</p>}
                    {r.notes && <p className="muted">{r.notes}</p>}
                  </div>
                ))}
                {!detail.records.length && <Empty>No records yet.</Empty>}
              </div>
              <h3 className="gap">Visits</h3>
              <div className="stack tight">
                {detail.appointments.map((a) => (
                  <div className="row-item" key={a.id}>
                    <div className="when"><b>{hm(a.slot_time)}</b><span>{fmtDate(a.appointment_date)}</span></div>
                    <div className="grow">{a.doctor_name}<span className="muted"> · {a.department_name}</span></div>
                    <Chip status={a.status} />
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}

const blankDoc = { full_name: "", department_id: "", qualification: "", experience_years: 0, consultation_fee: 500, available_days: "Mon,Tue,Wed,Thu,Fri", start_time: "09:00", end_time: "17:00", slot_minutes: 30 };

export function AdminDoctors() {
  const [docs, setDocs] = useState([]);
  const [deps, setDeps] = useState([]);
  const [f, setF] = useState(blankDoc);
  const [editing, setEditing] = useState(null);
  const [msg, setMsg] = useState({});
  const load = () => api.get("/doctors").then(setDocs);
  useEffect(() => { load(); api.get("/departments").then(setDeps); }, []);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const days = f.available_days.split(",").filter(Boolean);
  const toggleDay = (d) => setF({ ...f, available_days: DAYS.filter((x) => (x === d ? !days.includes(d) : days.includes(x))).join(",") });
  const edit = (d) => { setEditing(d.id); setMsg({}); setF({ ...d, start_time: hm(d.start_time), end_time: hm(d.end_time), qualification: d.qualification || "" }); window.scrollTo(0, 0); };
  const reset = () => { setEditing(null); setF(blankDoc); };
  const submit = async (e) => {
    e.preventDefault();
    const body = { full_name: f.full_name, department_id: Number(f.department_id), qualification: f.qualification || null, experience_years: Number(f.experience_years), consultation_fee: Number(f.consultation_fee), available_days: f.available_days, start_time: f.start_time, end_time: f.end_time, slot_minutes: Number(f.slot_minutes) };
    try {
      if (editing) await api.put(`/doctors/${editing}`, body); else await api.post("/doctors", body);
      setMsg({ ok: editing ? "Doctor updated" : "Doctor added" }); reset(); load();
    } catch (x) { setMsg({ error: x.message }); }
  };
  const remove = async (d) => {
    if (!confirm(`Remove ${d.full_name} from booking? Past appointments are kept.`)) return;
    await api.del(`/doctors/${d.id}`); load();
  };
  return (
    <>
      <h2>Doctors</h2>
      <form className="panel" onSubmit={submit}>
        <h3>{editing ? "Edit doctor" : "Add a doctor"}</h3>
        <Alert {...msg} />
        <div className="two">
          <Field label="Name"><input required value={f.full_name} onChange={set("full_name")} /></Field>
          <Field label="Department">
            <select required value={f.department_id} onChange={set("department_id")}><option value="">Choose</option>{deps.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}</select>
          </Field>
          <Field label="Qualification"><input value={f.qualification} onChange={set("qualification")} /></Field>
          <Field label="Experience (years)"><input type="number" min="0" max="60" value={f.experience_years} onChange={set("experience_years")} /></Field>
          <Field label="Consultation fee (₹)"><input type="number" min="0" value={f.consultation_fee} onChange={set("consultation_fee")} /></Field>
          <Field label="Slot length (minutes)"><input type="number" min="10" max="120" step="5" value={f.slot_minutes} onChange={set("slot_minutes")} /></Field>
          <Field label="Starts"><input type="time" required value={f.start_time} onChange={set("start_time")} /></Field>
          <Field label="Ends"><input type="time" required value={f.end_time} onChange={set("end_time")} /></Field>
        </div>
        <p className="label">Available days</p>
        <div className="days">{DAYS.map((d) => <label key={d} className={days.includes(d) ? "on" : ""}><input type="checkbox" checked={days.includes(d)} onChange={() => toggleDay(d)} />{d}</label>)}</div>
        <div className="row"><button className="btn" disabled={!days.length}>{editing ? "Save changes" : "Add doctor"}</button>{editing && <button type="button" className="btn ghost" onClick={reset}>Cancel edit</button>}</div>
      </form>
      <div className="scroll"><table>
        <thead><tr><th>Doctor</th><th>Department</th><th>Schedule</th><th>Fee</th><th></th></tr></thead>
        <tbody>{docs.map((d) => (
          <tr key={d.id}>
            <td><b>{d.full_name}</b><br /><span className="muted">{d.qualification} · {d.experience_years} yrs</span></td>
            <td>{d.department_name}</td>
            <td>{d.available_days.split(",").join(", ")}<br /><span className="muted">{hm(d.start_time)}–{hm(d.end_time)}, {d.slot_minutes} min slots</span></td>
            <td>₹{d.consultation_fee}</td>
            <td className="actions"><button className="btn small ghost" onClick={() => edit(d)}>Edit</button><button className="btn small ghost" onClick={() => remove(d)}>Remove</button></td>
          </tr>))}
        </tbody>
      </table></div>
    </>
  );
}

export function AdminDepartments() {
  const [deps, setDeps] = useState([]);
  const [f, setF] = useState({ name: "", description: "" });
  const [editing, setEditing] = useState(null);
  const [msg, setMsg] = useState({});
  const load = () => api.get("/departments").then(setDeps);
  useEffect(() => { load(); }, []);
  const submit = async (e) => {
    e.preventDefault();
    const body = { name: f.name, description: f.description || null };
    try {
      if (editing) await api.put(`/departments/${editing}`, body); else await api.post("/departments", body);
      setMsg({ ok: editing ? "Department updated" : "Department added" }); setEditing(null); setF({ name: "", description: "" }); load();
    } catch (x) { setMsg({ error: x.message }); }
  };
  const remove = async (d) => {
    if (!confirm(`Delete ${d.name}?`)) return;
    try { await api.del(`/departments/${d.id}`); setMsg({ ok: "Department deleted" }); load(); } catch (x) { setMsg({ error: x.message }); }
  };
  return (
    <>
      <h2>Departments</h2>
      <form className="panel" onSubmit={submit}>
        <h3>{editing ? "Edit department" : "Add a department"}</h3>
        <Alert {...msg} />
        <Field label="Name"><input required minLength={2} value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} /></Field>
        <Field label="Description"><textarea rows={2} value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })} /></Field>
        <div className="row"><button className="btn">{editing ? "Save changes" : "Add department"}</button>{editing && <button type="button" className="btn ghost" onClick={() => { setEditing(null); setF({ name: "", description: "" }); }}>Cancel edit</button>}</div>
      </form>
      <ul className="index">
        {deps.map((d) => (
          <li key={d.id}>
            <strong>{d.name}</strong><span>{d.description}</span>
            <span className="actions"><button className="btn small ghost" onClick={() => { setEditing(d.id); setF({ name: d.name, description: d.description || "" }); window.scrollTo(0, 0); }}>Edit</button><button className="btn small ghost" onClick={() => remove(d)}>Delete</button></span>
          </li>
        ))}
      </ul>
    </>
  );
}
