import { createContext, useContext, useState } from "react";

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("user") || "null"));
  const save = (t) => {
    const u = { role: t.role, full_name: t.full_name };
    localStorage.setItem("token", t.access_token);
    localStorage.setItem("user", JSON.stringify(u));
    setUser(u);
  };
  const logout = () => {
    localStorage.clear();
    setUser(null);
  };
  return <Ctx.Provider value={{ user, save, logout }}>{children}</Ctx.Provider>;
}
