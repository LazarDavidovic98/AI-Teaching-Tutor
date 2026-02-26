/**
 * ChatPage – Glavni tutor chat interfejs
 * ========================================
 * Funkcionalnosti:
 *  - Prikaz poruka sa Markdown + KaTeX renderovanjem (matematičke formule)
 *  - Odabir predmeta (matematika / ML / opšte)
 *  - Prikazivanje izvora iz RAG-a ispod svakog odgovora
 *  - Auto-scroll na najnoviju poruku
 *  - Streaming efekt (typing indicator dok čeka odgovor)
 */

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { Send, Bot, User, BookOpen, Loader2 } from "lucide-react";
import api from "../services/api";
import toast from "react-hot-toast";

// Dostupni predmeti za filtriranje RAG pretrage
const SUBJECTS = [
  { value: "general",  label: "Opšte",           emoji: "🌐" },
  { value: "math",     label: "Matematika",       emoji: "📐" },
  { value: "ml",       label: "Mašinsko učenje",  emoji: "🤖" },
  { value: "calculus", label: "Analiza",           emoji: "∫" },
  { value: "algebra",  label: "Algebra",           emoji: "🔣" },
];

// Komponenta za jednu poruku u chatu
function ChatBubble({ message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex gap-3 chat-bubble ${isUser ? "justify-end" : "justify-start"}`}>
      {/* Avatar za AI */}
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}

      <div className={`max-w-[78%] ${isUser ? "order-first" : ""}`}>
        {/* Balon poruke */}
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? "bg-gradient-to-br from-primary-600 to-accent-600 text-white rounded-tr-sm"
              : "bg-slate-800 text-slate-200 border border-slate-700/50 rounded-tl-sm"
          }`}
        >
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            // Markdown + KaTeX za AI odgovore
            <ReactMarkdown
              remarkPlugins={[remarkMath]}
              rehypePlugins={[rehypeKatex]}
              components={{
                // Stilizovani code blokovi
                code({ inline, children }) {
                  return inline ? (
                    <code className="bg-slate-700 text-accent-300 px-1.5 py-0.5 rounded font-mono text-xs">
                      {children}
                    </code>
                  ) : (
                    <pre className="bg-slate-900 border border-slate-700 rounded-xl p-4 overflow-x-auto mt-3 mb-1">
                      <code className="text-xs font-mono text-slate-300">{children}</code>
                    </pre>
                  );
                },
                // Stilizovane liste
                ul({ children }) { return <ul className="list-disc list-inside space-y-1 mt-2">{children}</ul>; },
                ol({ children }) { return <ol className="list-decimal list-inside space-y-1 mt-2">{children}</ol>; },
                // Bold tekst
                strong({ children }) { return <strong className="text-primary-300 font-semibold">{children}</strong>; },
                // Naslovi
                h3({ children }) { return <h3 className="text-base font-semibold text-white mt-3 mb-1">{children}</h3>; },
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Prikaz izvora (samo za AI poruke) */}
        {!isUser && message.sources?.length > 0 && (
          <div className="mt-2 space-y-1">
            {message.sources.map((src, i) => (
              <div
                key={i}
                className="flex items-start gap-2 px-3 py-2 bg-slate-900/80 border border-slate-700/30 rounded-lg text-xs text-slate-500"
              >
                <BookOpen className="w-3 h-3 mt-0.5 text-primary-500 flex-shrink-0" />
                <span className="line-clamp-2">{src}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Avatar za korisnika */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
          <User className="w-4 h-4 text-slate-300" />
        </div>
      )}
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Zdravo! 👋 Ja sam vaš AI tutor za matematiku i mašinsko učenje.\n\nMožete mi postavljati pitanja, tražiti objašnjenja korak po korak, ili otpremiti materijale pa da ih zajedno analiziramo.\n\nŠta vas zanima danas?",
      sources: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [subject, setSubject] = useState("general");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll na novu poruku
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: "user", content: input.trim(), sources: [] };
    const currentInput = input.trim();
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.post("/api/chat/ask", {
        message: currentInput,
        history: messages.slice(-6).map(({ role, content }) => ({ role, content })),
        subject,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.data.answer,
          sources: res.data.sources,
        },
      ]);
    } catch (err) {
      toast.error("Greška pri komunikaciji sa serverom.");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Žao mi je, došlo je do greške. Pokušajte ponovo.",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const currentSubject = SUBJECTS.find((s) => s.value === subject);

  return (
    <div className="flex flex-col h-screen">
      {/* Zaglavlje */}
      <header className="px-6 py-4 border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-white">Tutor Chat</h1>
          <p className="text-xs text-slate-500">RAG-powered AI asistent</p>
        </div>

        {/* Odabir predmeta */}
        <div className="relative">
          <div className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl cursor-pointer">
            <span className="text-sm">{currentSubject?.emoji}</span>
            <select
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="bg-transparent text-slate-300 text-sm font-medium cursor-pointer focus:outline-none pr-1"
            >
              {SUBJECTS.map((s) => (
                <option key={s.value} value={s.value} className="bg-slate-800">
                  {s.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      {/* Poruke */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
        {messages.map((msg, i) => (
          <ChatBubble key={i} message={msg} />
        ))}

        {/* Typing indicator dok čeka odgovor */}
        {loading && (
          <div className="flex gap-3 items-start chat-bubble">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="px-4 py-3 bg-slate-800 border border-slate-700/50 rounded-2xl rounded-tl-sm">
              <div className="flex gap-1.5 items-center h-4">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-1.5 h-1.5 rounded-full bg-primary-400 animate-bounce"
                    style={{ animationDelay: `${i * 150}ms` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input forma */}
      <div className="px-6 py-4 border-t border-slate-800 bg-slate-900/50 backdrop-blur-sm">
        <div className="flex gap-3 items-end max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Postavljajte pitanja o matematici i mašinskom učenju... (Enter za slanje)"
              rows={1}
              className="w-full px-4 py-3 pr-12 bg-slate-800 border border-slate-700 rounded-2xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/50 transition-colors text-sm resize-none"
              style={{ minHeight: "48px", maxHeight: "160px" }}
              onInput={(e) => {
                e.target.style.height = "auto";
                e.target.style.height = Math.min(e.target.scrollHeight, 160) + "px";
              }}
            />
          </div>

          {/* Dugme za slanje */}
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="flex-shrink-0 w-12 h-12 flex items-center justify-center bg-gradient-to-br from-primary-600 to-accent-600 hover:from-primary-500 hover:to-accent-500 text-white rounded-2xl transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-primary-500/20"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        <p className="text-center text-xs text-slate-600 mt-2">
          Shift+Enter za novi red • Enter za slanje
        </p>
      </div>
    </div>
  );
}
