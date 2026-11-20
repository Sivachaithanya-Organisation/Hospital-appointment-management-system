import { Link, Navigate, NavLink, Outlet, Route, Routes, useNavigate } from "react-router-dom";
import { useAuth } from "./auth";
import { Home, Login, Signup } from "./pages/Public";
import { Book, MyAppointments, Records } from "./pages/Patient";
import { AdminAppointments, AdminDepartments, AdminDoctors, AdminPatients, AdminShell, Overview } from "./pages/Admin";

function Guard({ role }) {
  const { user } = useAuth();
  if (!user) return <Navigate to={role === "admin" ? "/admin/login" : "/login"} replace />;
  if (user.role !== role) return <Navigate to="/" replace />;
  return <Outlet />;
}

function Nav() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  return (
    <header className="nav">
      <Link to="/" className="brand">City<b>Care</b></Link>
      <nav>
        {user?.role === "patient" && (
          <>
            <NavLink to="/patient" end>My appointments</NavLink>
            <NavLink to="/patient/book">Book a visit</NavLink>
            <NavLink to="/patient/records">My records</NavLink>
          </>
        )}
        {user?.role === "admin" && <NavLink to="/admin">Admin console</NavLink>}
        {user ? (
          <button className="btn small ghost" onClick={() => { logout(); nav("/"); }}>
            Sign out ({user.full_name.split(" ")[0]})
          </button>
        ) : (
          <>
            <NavLink to="/login">Patient login</NavLink>
            <NavLink to="/admin/login">Admin</NavLink>
          </>
        )}
      </nav>
    </header>
  );
}

export default function App() {
  return (
    <>
      <Nav />
      <main className="page">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/admin/login" element={<Login admin />} />
          <Route element={<Guard role="patient" />}>
            <Route path="/patient" element={<MyAppointments />} />
            <Route path="/patient/book" element={<Book />} />
            <Route path="/patient/records" element={<Records />} />
          </Route>
          <Route element={<Guard role="admin" />}>
            <Route path="/admin" element={<AdminShell />}>
              <Route index element={<Overview />} />
              <Route path="appointments" element={<AdminAppointments />} />
              <Route path="patients" element={<AdminPatients />} />
              <Route path="doctors" element={<AdminDoctors />} />
              <Route path="departments" element={<AdminDepartments />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  );
}
