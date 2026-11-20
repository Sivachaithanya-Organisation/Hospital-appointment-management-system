import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { Alert, Chip, Empty, Field, fmtDate, hm, isoDate } from "../ui";

export function MyAppointments() {
  const [rows, setRows] = useState(null);
  const [err, setErr] = useState("");
  const load = () => api.get("/appointments/me").then(setRows).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);
  const cancel = async (id) => {
    if (!confirm("Cancel this appointment?")) return;
    try { await api.post(`/appointments/${id}/cancel`); load(); } catch (e) { setErr(e.message); }
  };
  return (
    <>
      <div className="head"><h2>My appointments</h2><Link className="btn" to="/patient/book">Book a visit</Link></div>
      <Alert error={err} />
      {rows && !rows.length && <Empty>No appointments yet. Book your first visit to get started.</Empty>}
      <div className="stack">
        {rows?.map((a) => (
          <div className="row-item" key={a.id}>
            <div className="when"><b>{hm(a.slot_time)}</b><span>{fmtDate(a.appointment_date)}</span></div>
            <div className="grow"><b>{a.doctor_name}</b><span className="muted"> · {a.department_name}</span>{a.reason && <p className="muted">{a.reason}</p>}</div>
            <Chip status={a.status} />
            {a.status === "booked" && <button className="btn small ghost" onClick={() => cancel(a.id)}>Cancel</button>}
          </div>
        ))}
      </div>
    </>
  );
}

export function Book() {
  const nav = useNavigate();
  const [deps, setDeps] = useState([]);
  const [docs, setDocs] = useState([]);
  const [dep, setDep] = useState("");
  const [doc, setDoc] = useState(null);
  const [date, setDate] = useState("");
  const [slots, setSlots] = useState([]);
  const [slot, setSlot] = useState("");
  const [reason, setReason] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const today = useMemo(() => new Date(), []);
  const max = useMemo(() => isoDate(new Date(today.getTime() + 60 * 864e5)), [today]);

  useEffect(() => { api.get("/departments").then(setDeps); }, []);
  useEffect(() => {
    setDoc(null); setDocs([]);
    if (dep) api.get(`/doctors?department_id=${dep}`).then(setDocs);
  }, [dep]);
  useEffect(() => {
    setSlot(""); setSlots([]);
    if (doc && date) api.get(`/doctors/${doc.id}/slots?date=${date}`).then((r) => setSlots(r.slots)).catch((e) => setErr(e.message));
  }, [doc, date]);

  const confirmBooking = async () => {
    setErr(""); setBusy(true);
    try {
      await api.post("/appointments", { doctor_id: doc.id, appointment_date: date, slot_time: slot, reason: reason || null });
      nav("/patient");
    } catch (e) {
      setErr(e.message); setBusy(false);
      api.get(`/doctors/${doc.id}/slots?date=${date}`).then((r) => setSlots(r.slots));
    }
  };

  return (
    <>
      <h2>Book a visit</h2>
      <Alert error={err} />
      <div className="panel">
        <Field label="1. Department">
          <select value={dep} onChange={(e) => setDep(e.target.value)}>
            <option value="">Choose a department</option>
            {deps.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </Field>
        {dep && (
          <>
            <p className="label">2. Doctor</p>
            <div className="doctors">
              {docs.map((d) => (
                <button type="button" key={d.id} className={`doc ${doc?.id === d.id ? "on" : ""}`} onClick={() => setDoc(d)}>
                  <b>{d.full_name}</b>
                  <span>{d.qualification}</span>
                  <span>{d.experience_years} yrs · ₹{d.consultation_fee}</span>
                  <span>{d.available_days.split(",").join(", ")}</span>
                </button>
              ))}
            </div>
          </>
        )}
        {doc && (
          <Field label="3. Date">
            <input type="date" value={date} min={isoDate(today)} max={max} onChange={(e) => setDate(e.target.value)} />
          </Field>
        )}
        {doc && date && (
          <>
            <p className="label">4. Time slot</p>
            {!slots.length ? <Empty>{doc.full_name} does not see patients on this day. Try another date.</Empty> : (
              <div className="slots">
                {slots.map((s) => (
                  <button type="button" key={s.time} disabled={!s.available} className={`slot ${slot === s.time ? "on" : ""}`} onClick={() => setSlot(s.time)}>
                    {s.time}
                  </button>
                ))}
              </div>
            )}
          </>
        )}
        {slot && (
          <>
            <Field label="Reason for visit (optional)"><textarea rows={2} maxLength={500} value={reason} onChange={(e) => setReason(e.target.value)} /></Field>
            <button className="btn" disabled={busy} onClick={confirmBooking}>Confirm {fmtDate(date)} at {slot}</button>
          </>
        )}
      </div>
    </>
  );
}

export function Records() {
  const [p, setP] = useState(null);
  const [records, setRecords] = useState(null);
  const [msg, setMsg] = useState({});
  useEffect(() => {
    api.get("/patients/me").then(setP);
    api.get("/patients/me/records").then(setRecords);
  }, []);
  const set = (k) => (e) => setP({ ...p, [k]: e.target.value });
  const save = async (e) => {
    e.preventDefault();
    const { full_name, phone, dob, gender, blood_group, address } = p;
    try {
      const nb = (v) => (v === "" ? null : v);
      setP(await api.put("/patients/me", { full_name, phone: nb(phone), dob: nb(dob), gender: nb(gender), blood_group: nb(blood_group), address: nb(address) }));
      setMsg({ ok: "Profile saved" });
    } catch (x) { setMsg({ error: x.message }); }
  };
  if (!p) return null;
  return (
    <>
      <h2>My records</h2>
      <form className="panel" onSubmit={save}>
        <h3>Profile</h3>
        <Alert {...msg} />
        <div className="two">
          <Field label="Full name"><input required value={p.full_name} onChange={set("full_name")} /></Field>
          <Field label="Email"><input disabled value={p.email} /></Field>
          <Field label="Phone"><input value={p.phone || ""} onChange={set("phone")} /></Field>
          <Field label="Date of birth"><input type="date" value={p.dob || ""} onChange={set("dob")} /></Field>
          <Field label="Gender">
            <select value={p.gender || ""} onChange={set("gender")}><option value="">Prefer not to say</option><option>Female</option><option>Male</option><option>Other</option></select>
          </Field>
          <Field label="Blood group">
            <select value={p.blood_group || ""} onChange={set("blood_group")}><option value="">Unknown</option>{["A+","A-","B+","B-","AB+","AB-","O+","O-"].map((b) => <option key={b}>{b}</option>)}</select>
          </Field>
        </div>
        <Field label="Address"><textarea rows={2} value={p.address || ""} onChange={set("address")} /></Field>
        <button className="btn">Save profile</button>
      </form>
      <h3 className="gap">Medical history</h3>
      {records && !records.length && <Empty>No records yet. Diagnoses and prescriptions added by the hospital will show up here.</Empty>}
      <div className="stack">
        {records?.map((r) => (
          <div className="record" key={r.id}>
            <div className="muted">{new Date(r.created_at).toLocaleDateString()}{r.doctor_name && ` · ${r.doctor_name}`}</div>
            <p><b>Diagnosis:</b> {r.diagnosis}</p>
            {r.prescription && <p><b>Prescription:</b> {r.prescription}</p>}
            {r.notes && <p className="muted">{r.notes}</p>}
          </div>
        ))}
      </div>
    </>
  );
}
