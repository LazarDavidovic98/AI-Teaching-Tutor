/**
 * UploadPage – Upravljanje nastavnim materijalima
 * =================================================
 * Funkcionalnosti:
 *  - Drag & drop upload PDF/txt fajlova
 *  - Odabir predmeta i opis dokumenta
 *  - Lista otpremljenih dokumenata sa chunk statistikom
 *  - Brisanje dokumenata (iz DB-a i vektorske baze)
 */

import { useState, useEffect, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import {
  Upload, FileText, Trash2, Loader2, BookOpen,
  CheckCircle, AlertCircle, ChevronDown,
} from "lucide-react";
import api from "../services/api";
import toast from "react-hot-toast";

const SUBJECTS = [
  { value: "general",  label: "Opšte" },
  { value: "math",     label: "Matematika" },
  { value: "ml",       label: "Mašinsko učenje" },
  { value: "calculus", label: "Analiza" },
  { value: "algebra",  label: "Algebra" },
];

// Formatiranje veličine fajla u čitljiv format
function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// Kartica za prikaz jednog dokumenta
function DocumentCard({ doc, onDelete }) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm(`Obrisati dokument "${doc.original_name}"?`)) return;
    setDeleting(true);
    try {
      await api.delete(`/api/upload/${doc.id}`);
      toast.success("Dokument je obrisan.");
      onDelete(doc.id);
    } catch {
      toast.error("Greška pri brisanju dokumenta.");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="glass-card p-4 flex items-start gap-4 hover:border-slate-600/50 transition-colors">
      {/* Ikona fajla */}
      <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-primary-500/20 border border-primary-500/30 flex items-center justify-center">
        <FileText className="w-5 h-5 text-primary-400" />
      </div>

      {/* Informacije */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-200 truncate">{doc.original_name}</p>
        <div className="flex flex-wrap gap-3 mt-1.5">
          <span className="text-xs text-slate-500">{formatBytes(doc.file_size_bytes)}</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-primary-500/15 text-primary-400 border border-primary-500/20">
            {SUBJECTS.find((s) => s.value === doc.subject)?.label ?? doc.subject}
          </span>
          <span className="text-xs text-slate-500">
            {doc.chunk_count} chunk-ova indeksirano
          </span>
        </div>
        {doc.description && (
          <p className="text-xs text-slate-600 mt-1 line-clamp-1">{doc.description}</p>
        )}
      </div>

      {/* Datum + brisanje */}
      <div className="flex-shrink-0 flex items-center gap-3">
        <span className="text-xs text-slate-600 hidden sm:block">
          {new Date(doc.created_at).toLocaleDateString("sr-Latn-BA")}
        </span>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="p-2 rounded-lg text-slate-600 hover:text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50"
          title="Obriši dokument"
        >
          {deleting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}

export default function UploadPage() {
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [subject, setSubject] = useState("general");
  const [description, setDescription] = useState("");
  const [uploadStatus, setUploadStatus] = useState(null); // "success" | "error" | null

  // Učitaj listu dokumenata pri otvaranju stranice
  useEffect(() => {
    api.get("/api/upload/documents")
      .then((res) => setDocuments(res.data))
      .catch(() => toast.error("Greška pri učitavanju dokumenata."))
      .finally(() => setLoadingDocs(false));
  }, []);

  // React Dropzone konfiguracija
  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setUploadStatus(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("subject", subject);
    formData.append("description", description);

    try {
      const res = await api.post("/api/upload/file", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setDocuments((prev) => [res.data, ...prev]);
      setUploadStatus("success");
      setDescription("");
      toast.success(`"${file.name}" je uspješno otpremljen i indeksiran!`);
    } catch (err) {
      setUploadStatus("error");
      toast.error(err.response?.data?.detail ?? "Greška pri otpremanju fajla.");
    } finally {
      setUploading(false);
    }
  }, [subject, description]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "text/plain": [".txt"] },
    maxFiles: 1,
    disabled: uploading,
  });

  const handleDeleteDoc = (docId) => {
    setDocuments((prev) => prev.filter((d) => d.id !== docId));
  };

  return (
    <div className="flex flex-col h-screen overflow-y-auto">
      {/* Zaglavlje */}
      <header className="px-6 py-4 border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm">
        <h1 className="text-lg font-semibold text-white">Nastavni materijali</h1>
        <p className="text-xs text-slate-500">Otpremajte PDF i TXT fajlove – automatski se indeksiraju u RAG sistem</p>
      </header>

      <div className="flex-1 px-6 py-6 max-w-3xl w-full mx-auto space-y-6">
        {/* Panel za upload */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-slate-300 mb-4">Otpremi novi materijal</h2>

          {/* Metadata forma */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">Predmet</label>
              <select
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-slate-200 text-sm focus:outline-none focus:border-primary-500 transition-colors"
              >
                {SUBJECTS.map((s) => (
                  <option key={s.value} value={s.value} className="bg-slate-800">
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">Opis (opciono)</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Kratki opis sadržaja..."
                className="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-slate-200 text-sm placeholder-slate-500 focus:outline-none focus:border-primary-500 transition-colors"
              />
            </div>
          </div>

          {/* Dropzone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 ${
              isDragActive && !isDragReject
                ? "border-primary-500 bg-primary-500/10"
                : isDragReject
                ? "border-red-500 bg-red-500/10"
                : "border-slate-700 hover:border-primary-500/50 hover:bg-slate-800/50"
            } ${uploading ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center gap-3">
              {uploading ? (
                <>
                  <Loader2 className="w-10 h-10 text-primary-400 animate-spin" />
                  <p className="text-sm text-slate-400">Otpremanje i indeksiranje u toku...</p>
                  <p className="text-xs text-slate-600">Ovo može potrajati za veće fajlove</p>
                </>
              ) : uploadStatus === "success" ? (
                <>
                  <CheckCircle className="w-10 h-10 text-green-400" />
                  <p className="text-sm text-green-400 font-medium">Uspješno otpremljeno!</p>
                  <p className="text-xs text-slate-500">Prevucite novi fajl ili kliknite</p>
                </>
              ) : (
                <>
                  <div className="p-3 rounded-2xl bg-slate-800 border border-slate-700">
                    <Upload className="w-8 h-8 text-primary-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-300">
                      {isDragActive ? "Otpustite fajl ovdje" : "Prevucite fajl ili kliknite za odabir"}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">Podržani formati: PDF, TXT • Max 20 MB</p>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Lista dokumenata */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-slate-300">
              Vaši materijali
            </h2>
            <span className="text-xs text-slate-500 bg-slate-800 px-2.5 py-1 rounded-full">
              {documents.length} dokumenata
            </span>
          </div>

          {loadingDocs ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 text-primary-400 animate-spin" />
            </div>
          ) : documents.length === 0 ? (
            <div className="glass-card p-12 text-center">
              <BookOpen className="w-12 h-12 text-slate-700 mx-auto mb-3" />
              <p className="text-slate-500 text-sm">Nema otpremljenih materijala</p>
              <p className="text-slate-600 text-xs mt-1">Otpremite PDF ili TXT fajl da počnete</p>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => (
                <DocumentCard key={doc.id} doc={doc} onDelete={handleDeleteDoc} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
