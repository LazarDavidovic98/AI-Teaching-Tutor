/**
 * Layout – Navigacijska traka + sadržaj stranice
 * ================================================
 * Koristi se za sve zaštićene stranice (Chat, Upload).
 * Sadrži sidebar navigaciju i zaglavlje sa informacijom o korisniku.
 */

import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { MessageCircle, Upload, LogOut, Brain } from "lucide-react";
import toast from "react-hot-toast";

const navItems = [
  { to: "/chat",   label: "Tutor chat",      icon: MessageCircle },
  { to: "/upload", label: "Materijali",       icon: Upload },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success("Uspješno ste se odjavili.");
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen bg-slate-950">
      {/* Sidebar */}
      <aside className="w-64 flex flex-col bg-slate-900 border-r border-slate-800">
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-800">
          <div className="p-2 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <span className="font-semibold text-white text-sm leading-tight">
            AI Teaching<br />
            <span className="gradient-text font-bold">Tutor</span>
          </span>
        </div>

        {/* Navigacione stavke */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-primary-500/20 text-primary-300 border border-primary-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }`
              }
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Korisnik + odjava */}
        <div className="px-3 py-4 border-t border-slate-800">
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-800/50 mb-2">
            {/* Avatar sa inicijalima */}
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-xs font-bold text-white">
              {user?.username?.[0]?.toUpperCase() ?? "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-200 truncate">{user?.username}</p>
              <p className="text-xs text-slate-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-4 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200"
          >
            <LogOut className="w-4 h-4" />
            Odjavi se
          </button>
        </div>
      </aside>

      {/* Glavni sadržaj */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
