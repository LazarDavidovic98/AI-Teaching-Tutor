/**
 * AuthContext – globalno stanje autentifikacije
 * ================================================
 * Čuva JWT token u localStorage i pruža ga svim komponentama
 * putem React Context API-ja.
 * Na svakom refreshu stranice token se čita iz localStorage
 * i axios interceptor ga automatski šalje u svaki API zahtjev.
 */

import { createContext, useContext, useState, useEffect } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);  // čeka dok se token ne provjeri

  // Pri pokretanju aplikacije provjeri da li postoji token u localStorage
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      // Dohvati podatke o korisniku sa API-ja
      api.get("/api/auth/me")
        .then((res) => setUser(res.data))
        .catch(() => localStorage.removeItem("token"))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await api.post("/api/auth/login", { email, password });
    localStorage.setItem("token", res.data.access_token);
    // Nakon uspješne prijave dohvati profil korisnika
    const profile = await api.get("/api/auth/me");
    setUser(profile.data);
  };

  const register = async (email, username, password) => {
    await api.post("/api/auth/register", { email, username, password });
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Konvenijentan hook za korištenje auth konteksta
export const useAuth = () => useContext(AuthContext);
