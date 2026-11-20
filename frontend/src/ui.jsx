export const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
export const hm = (t) => (t ? t.slice(0, 5) : "");
export const fmtDate = (d) =>
  new Date(d + "T00:00").toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short", year: "numeric" });
export const isoDate = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);

export const Field = ({ label, children }) => (
  <label className="field">
    <span>{label}</span>
    {children}
  </label>
);
export const Chip = ({ status }) => <span className={`chip ${status}`}>{status}</span>;
export const Alert = ({ error, ok }) =>
  error ? <div className="alert bad">{error}</div> : ok ? <div className="alert ok">{ok}</div> : null;
export const Empty = ({ children }) => <p className="empty">{children}</p>;
