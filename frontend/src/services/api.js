/**
 * Axios instanca – centralno mjesto za API komunikaciju
 * ======================================================
 * Interceptor automatski dodaje Authorization header sa JWT tokenom
 * u svaki zahtjev koji se šalje ka backendu.
 */

import axios from "axios";

const api = axios.create({
  baseURL: "",  // Vite proxy preusmjerava /api/* na localhost:8000
  headers: { "Content-Type": "application/json" },
});

// Request interceptor – dodaj token ako postoji
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor – pri 401 odjavi korisnika
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
