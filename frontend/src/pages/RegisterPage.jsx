/**
 * Stranica za registraciju
 * =========================
 * Prikuplja email, korisničko ime i lozinku.
 * Nakon uspješne registracije preusmjerava na /login.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Brain, Mail, Lock, User, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", username: "", password: "", confirm: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirm) {
      setError("Lozinke se ne podudaraju.");
      return;
    }
    if (form.password.length < 6) {
      setError("Lozinka mora imati najmanje 6 karaktera.");
      return;
    }

    setLoading(true);
    try {
      await register(form.email, form.username, form.password);
      toast.success("Nalog kreiran! Prijavite se.");
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail ?? "Greška pri registraciji.");
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { key: "email",    label: "Email adresa",      type: "email",    icon: Mail,  placeholder: "vas@email.com" },
    { key: "username", label: "Korisničko ime",     type: "text",     icon: User,  placeholder: "vas_username" },
    { key: "password", label: "Lozinka",            type: "password", icon: Lock,  placeholder: "••••••••" },
    { key: "confirm",  label: "Potvrdi lozinku",    type: "password", icon: Lock,  placeholder: "••••••••" },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 px-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 mb-4 shadow-lg shadow-primary-500/25">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">AI Teaching Tutor</h1>
          <p className="text-slate-400 mt-2 text-sm">Kreirajte nalog i počnite učiti</p>
        </div>

        <div className="glass-card p-8">
          <h2 className="text-xl font-semibold text-white mb-6">Registracija</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {fields.map(({ key, label, type, icon: Icon, placeholder }) => (
              <div key={key}>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">{label}</label>
                <div className="relative">
                  <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type={type}
                    required
                    value={form[key]}
                    onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                    placeholder={placeholder}
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/50 transition-colors text-sm"
                  />
                </div>
              </div>
            ))}

            {error && (
              <div className="px-4 py-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-gradient-to-r from-primary-600 to-accent-600 hover:from-primary-500 hover:to-accent-500 text-white font-medium rounded-xl transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-primary-500/20 mt-2"
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Kreiranje naloga...</>
              ) : (
                "Napravite nalog"
              )}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-6">
            Već imate nalog?{" "}
            <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
              Prijavite se
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
