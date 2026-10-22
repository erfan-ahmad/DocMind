import { useState, useRef, useEffect } from "react";
import client from "../api/client";
import type { AskResponse } from "../types";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: AskResponse["sources"];
  timestamp: string;
}

export default function AI() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "سلام! من دستیار هوشمند DocMind هستم. با استفاده از فناوری RAG و مدل‌های پیشرفته، می‌توانم متن اسناد، گزارش‌ها و فایل‌های بارگذاری شده شما را جستجو و بر اساس آن‌ها به سوالات شما پاسخ دقیق دهم. چه سوالی دارید؟",
      timestamp: new Date().toLocaleTimeString("fa-IR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [selectedK, setSelectedK] = useState(5);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const samplePrompts = [
    "خلاصه‌ای از مهم‌ترین موضوعات در اسناد من ارائه بده.",
    "تعهدات و شروط مهم در قراردادها چیست؟",
    "چه نکات فنی یا راهبردی در گزارش‌های من مطرح شده است؟",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSend = async (questionText?: string) => {
    const question = (questionText || input).trim();
    if (!question || loading) return;

    setInput("");
    const userMsgId = Date.now().toString();
    const timeNow = new Date().toLocaleTimeString("fa-IR", {
      hour: "2-digit",
      minute: "2-digit",
    });

    setMessages((prev) => [
      ...prev,
      {
        id: userMsgId,
        role: "user",
        content: question,
        timestamp: timeNow,
      },
    ]);
    setLoading(true);

    try {
      const res = await client.post<AskResponse>("/ask/", {
        query: question,
        k: selectedK,
      });

      const assistantMsgId = (Date.now() + 1).toString();
      setMessages((prev) => [
        ...prev,
        {
          id: assistantMsgId,
          role: "assistant",
          content: res.data.answer || "پاسخی از اسناد شما یافت نشد.",
          sources: res.data.sources || [],
          timestamp: new Date().toLocaleTimeString("fa-IR", {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
    } catch (err: any) {
      console.error(err);
      const assistantMsgId = (Date.now() + 1).toString();
      const errorMsg =
        err?.response?.data?.error ||
        err?.response?.data?.message ||
        "متأسفانه در پردازش سوال شما یا برقراری ارتباط با مدل هوش مصنوعی خطایی رخ داد.";

      setMessages((prev) => [
        ...prev,
        {
          id: assistantMsgId,
          role: "assistant",
          content: `⚠️ ${errorMsg}`,
          timestamp: new Date().toLocaleTimeString("fa-IR", {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend();
  };

  return (
    <div className="max-w-5xl mx-auto flex flex-col h-[calc(100vh-140px)] min-h-[600px] animate-fadeIn">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-gray-100 dark:border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              گفتگو با اسناد و هوش مصنوعی
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-200 font-normal">
                فعال • RAG
              </span>
            </h1>
            <p className="text-xs text-gray-500 mt-0.5">
              پاسخ‌دهی دقیق بر مبنای محتوای اسناد بارگذاری شده شما
            </p>
          </div>
        </div>

        {/* Top Controls */}
        <div className="flex items-center gap-3 text-xs">
          <label className="text-gray-500 flex items-center gap-1.5 font-medium">
            <span>دقت جستجو (K):</span>
            <select
              value={selectedK}
              onChange={(e) => setSelectedK(Number(e.target.value))}
              className="bg-white border border-gray-200 rounded-lg px-2.5 py-1 text-gray-700 shadow-sm focus:ring-2 focus:ring-blue-500 outline-none"
            >
              <option value={3}>۳ تکه (سریع)</option>
              <option value={5}>۵ تکه (متعادل)</option>
              <option value={8}>۸ تکه (عمیق)</option>
            </select>
          </label>

          <button
            onClick={() =>
              setMessages([
                {
                  id: "welcome-reset",
                  role: "assistant",
                  content: "گفتگو پاک‌سازی شد. می‌توانید سوال جدیدی بپرسید.",
                  timestamp: new Date().toLocaleTimeString("fa-IR", {
                    hour: "2-digit",
                    minute: "2-digit",
                  }),
                },
              ])
            }
            className="text-gray-500 hover:text-red-600 p-2 hover:bg-gray-100 rounded-lg transition-colors title='پاک‌سازی تاریخچه گفتگو'"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto py-6 px-2 space-y-6">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3.5 ${
              msg.role === "user" ? "flex-row-reverse" : "flex-row"
            }`}
          >
            {/* Avatar */}
            <div
              className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 text-sm font-bold shadow-sm ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gradient-to-tr from-purple-600 to-indigo-600 text-white"
              }`}
            >
              {msg.role === "user" ? (
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              ) : (
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              )}
            </div>

            {/* Bubble Container */}
            <div
              className={`max-w-[85%] md:max-w-[75%] rounded-2xl p-4 shadow-sm relative group ${
                msg.role === "user"
                  ? "bg-blue-600 text-white rounded-tr-none"
                  : "bg-white border border-gray-100 text-gray-800 rounded-tl-none shadow-gray-100/70"
              }`}
            >
              {/* Message Content */}
              <p className="text-sm leading-relaxed whitespace-pre-wrap selection:bg-indigo-100 selection:text-indigo-900">
                {msg.content}
              </p>

              {/* Sources Accordion (If any) */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-4 pt-3 border-t border-gray-100 text-xs">
                  <div className="flex items-center gap-1.5 text-gray-500 font-semibold mb-2">
                    <svg
                      className="w-3.5 h-3.5 text-blue-500"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    <span>منابع استناد شده ({msg.sources.length} بخش):</span>
                  </div>

                  <div className="space-y-2">
                    {msg.sources.map((s, idx) => (
                      <details
                        key={idx}
                        className="group/details bg-gray-50 border border-gray-200/60 rounded-xl p-2.5 transition-all open:bg-blue-50/40 open:border-blue-200"
                      >
                        <summary className="cursor-pointer text-gray-700 flex items-center justify-between font-medium select-none">
                          <span className="flex items-center gap-1.5 truncate">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                            <span className="font-semibold text-gray-900">
                              {s.document_title}
                            </span>
                            <span className="text-gray-400">
                              • بخش {s.chunk_index}
                            </span>
                          </span>
                          <span className="text-[11px] px-1.5 py-0.5 rounded bg-gray-200 text-gray-700 font-mono">
                            امتیاز: {s.score.toFixed(3)}
                          </span>
                        </summary>
                        <div className="mt-2.5 pt-2 border-t border-gray-200 text-gray-600 text-xs leading-relaxed bg-white p-2 rounded-lg border border-gray-100">
                          {s.text}
                        </div>
                      </details>
                    ))}
                  </div>
                </div>
              )}

              {/* Timestamp & Actions */}
              <div
                className={`mt-2 flex items-center justify-between text-[11px] ${
                  msg.role === "user" ? "text-blue-100" : "text-gray-400"
                }`}
              >
                <span>{msg.timestamp}</span>
                <button
                  type="button"
                  onClick={() => handleCopy(msg.id, msg.content)}
                  className={`opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded ${
                    msg.role === "user"
                      ? "hover:bg-blue-700 text-white"
                      : "hover:bg-gray-100 text-gray-600"
                  }`}
                  title="کپی متن"
                >
                  {copiedId === msg.id ? (
                    <span>کپی شد! ✓</span>
                  ) : (
                    <>
                      <svg
                        className="w-3.5 h-3.5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                        />
                      </svg>
                      <span>کپی</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        ))}

        {/* Loading Spinner / Thinking state */}
        {loading && (
          <div className="flex items-start gap-3.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 text-white flex items-center justify-center shadow-sm">
              <svg
                className="w-5 h-5 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            </div>
            <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-none p-4 shadow-sm flex items-center gap-2">
              <span className="flex space-x-1.5 space-x-reverse">
                <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce"></span>
                <span
                  className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                ></span>
                <span
                  className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce"
                  style={{ animationDelay: "0.4s" }}
                ></span>
              </span>
              <span className="text-xs text-gray-500 font-medium">
                در حال جستجو در بردارها و تدوین پاسخ...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested prompts if few messages */}
      {messages.length <= 1 && (
        <div className="py-2">
          <p className="text-xs text-gray-400 font-medium mb-2">
            پیشنهادات برای شروع:
          </p>
          <div className="flex flex-wrap gap-2">
            {samplePrompts.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSend(prompt)}
                className="text-xs bg-gray-50 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 border border-gray-200 text-gray-600 rounded-xl px-3.5 py-2 transition-all text-right shadow-sm"
              >
                💬 {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <div className="pt-3 border-t border-gray-100">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="پرسش خود را درباره محتوای اسناد بنویسید..."
            disabled={loading}
            className="w-full pl-28 pr-5 py-3.5 bg-white border border-gray-200 rounded-2xl text-sm text-gray-800 placeholder-gray-400 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all disabled:bg-gray-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="absolute left-2 px-5 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-sm font-medium shadow-md shadow-blue-500/25 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
          >
            <span>ارسال</span>
            <svg
              className="w-4 h-4 transform rotate-180"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M14 5l7 7m0 0l-7 7m7-7H3"
              />
            </svg>
          </button>
        </form>
        <p className="text-[11px] text-gray-400 text-center mt-2">
          پاسخ‌ها توسط هوش مصنوعی و به صورت مستقیم از بخش‌های بازیافتی اسناد شما
          استخراج می‌شوند.
        </p>
      </div>
    </div>
  );
}