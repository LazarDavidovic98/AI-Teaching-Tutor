/**
 * App.jsx – Definicija ruta aplikacije
 * =====================================
 * Zaštićene rute preusmjeravaju na /login ako korisnik nije prijavljen.
 */

import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ChatPage from "./pages/ChatPage";
import UploadPage from "./pages/UploadPage";
import Layout from "./components/Layout";

// Komponenta koja štiti rute koje zahtijevaju prijavu
function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Javne rute */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Zaštićene rute – unutar Layout-a s navigacijom */}
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<Navigate to="/chat" replace />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="upload" element={<UploadPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
