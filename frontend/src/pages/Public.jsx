import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import { Alert, Field } from "../ui";

export function Home() {
  const { user } = useAuth();
  const [deps, setDeps] = useState([]);
  useEffect(() => { api.get("/departments").then(setDeps).catch(() => {}); }, []);
  return (
    <>
      <section className="hero">
        <h1>See the right doctor without waiting on hold.</h1>
        <p className="lead">
          Pick a department, choose a doctor, and take a free time slot. Your visits and medical records stay in one place.
        </p>
        <div className="row">
          {user ? (
            <Link className="btn" to={user.role === "admin" ? "/admin" : "/patient/book"}>
              {user.role === "admin" ? "Open admin console" : "Book a visit"}
            </Link>
          ) : (
            <>
              <Link className="btn" to="/signup">Create patient account</Link>
              <Link className="btn ghost" to="/login">Patient login</Link>
            </>
          )}
        </div>
      </section>
      <h2>Departments</h2>
      <ul className="index">
        {deps.map((d) => (
          <li key={d.id}>
            <strong>{d.name}</strong>
            <span>{d.description}</span>
          </li>
        ))}
      </ul>
    </>
  );
}

export function Login({ admin }) {
  const { save } = useAuth();
  const nav = useNavigate();
  const [f, setF] = useState(admin ? { email: "admin@hospital.com", password: "Admin@123" } : { email: "", password: "" });
  const [err, setErr] = useState("");
  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      save(await api.post(admin ? "/auth/admin/login" : "/auth/login", f, { auth: false }));
      nav(admin ? "/admin" : "/patient");
    } catch (x) { setErr(x.message); }
  };
  return (
    <form className="panel narrow" onSubmit={submit}>
      <h2>{admin ? "Admin sign in" : "Patient sign in"}</h2>
      {admin && <p className="muted">Guest admin details are pre-filled for now.</p>}
      <Alert error={err} />
      <Field label="Email"><input type="email" required value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></Field>
      <Field label="Password"><input type="password" required value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} /></Field>
      <button className="btn">Sign in</button>
      {!admin && <p className="muted">New here? <Link to="/signup">Create an account</Link></p>}
    </form>
  );
}

export function Signup() {
  const { save } = useAuth();
  const nav = useNavigate();
  const [f, setF] = useState({ full_name: "", email: "", password: "", phone: "", dob: "", gender: "", blood_group: "", address: "" });
  const [err, setErr] = useState("");
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    const body = Object.fromEntries(Object.entries(f).map(([k, v]) => [k, v === "" ? null : v]));
    try {
      save(await api.post("/auth/signup", body, { auth: false }));
      nav("/patient/book");
    } catch (x) { setErr(x.message); }
  };
  return (
    <form className="panel narrow" onSubmit={submit}>
      <h2>Create your patient account</h2>
      <Alert error={err} />
      <Field label="Full name"><input required minLength={2} value={f.full_name} onChange={set("full_name")} /></Field>
      <Field label="Email"><input type="email" required value={f.email} onChange={set("email")} /></Field>
      <Field label="Password (8+ characters)"><input type="password" required minLength={8} value={f.password} onChange={set("password")} /></Field>
      <div className="two">
        <Field label="Phone"><input value={f.phone} onChange={set("phone")} /></Field>
        <Field label="Date of birth"><input type="date" value={f.dob} onChange={set("dob")} /></Field>
        <Field label="Gender">
          <select value={f.gender} onChange={set("gender")}><option value="">Prefer not to say</option><option>Female</option><option>Male</option><option>Other</option></select>
        </Field>
        <Field label="Blood group">
          <select value={f.blood_group} onChange={set("blood_group")}><option value="">Unknown</option>{["A+","A-","B+","B-","AB+","AB-","O+","O-"].map((b) => <option key={b}>{b}</option>)}</select>
        </Field>
      </div>
      <Field label="Address"><textarea rows={2} value={f.address} onChange={set("address")} /></Field>
      <button className="btn">Create account</button>
      <p className="muted">Already registered? <Link to="/login">Sign in</Link></p>
    </form>
  );
}
