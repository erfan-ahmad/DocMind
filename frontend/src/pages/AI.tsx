import { useState } from "react";
import client from "../api/client";
import type { AskResponse } from "../types";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: AskResponse["sources"];
}

export default function AI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput("");
    setError("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const res = await client.post<AskResponse>("/ask/", {
        query: question,
        k: 5,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.data.answer,
          sources: res.data.sources,
        },
      ]);
    } catch (err: any) {
      console.error(err);
      setError("خطا در دریافت پاسخ.");
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "متأسفانه خطایی رخ داد." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">پرسش از اسناد</h1>

      <div className="bg-white rounded-lg shadow p-4 mb-4 min-h-[400px] max-h-[600px] overflow-y-auto">
        {messages.length === 0 ? (
          <p className="text-gray-400 text-center mt-20">
            سؤالی بپرسید تا از اسناد شما پاسخ داده شود.
          </p>
        ) : (
          <div className="space-y-6">
            {messages.map((msg, i) => (
              <div key={i}>
                {msg.role === "user" ? (
                  <div className="flex justify-end">
                    <div className="bg-blue-600 text-white px-4 py-2 rounded-lg max-w-[80%]">
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 px-4 py-2 rounded-lg max-w-[90%]">
                      <p className="whitespace-pre-wrap">{msg.content}</p>

                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-300">
                          <p className="text-xs text-gray-500 mb-2">
                            منابع:
                          </p>
                          <div className="space-y-2">
                            {msg.sources.map((s, j) => (
                              <details
                                key={j}
                                className="text-xs bg-white rounded p-2"
                              >
                                <summary className="cursor-pointer text-gray-700">
                                  {s.document_title} — Chunk {s.chunk_index} —
                                  امتیاز {s.score.toFixed(3)}
                                </summary>
                                <p className="mt-2 text-gray-600 whitespace-pre-wrap">
                                  {s.text}
                                </p>
                              </details>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 px-4 py-2 rounded-lg text-gray-500">
                  در حال فکر کردن...
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {error && <p className="text-red-600 mb-2 text-sm">{error}</p>}

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="سؤال خود را بنویسید..."
          className="flex-1 border border-gray-300 rounded px-4 py-2"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          ارسال
        </button>
      </form>
    </div>
  );
}