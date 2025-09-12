"use client";
import React, { useState } from "react";
import MessageBubble from "./MessageBubble";

type Msg = { role: "user" | "assistant"; text: string };

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);

  async function send() {
    if (!input.trim()) return;
    const userText = input.trim();
    setMessages((m) => [...m, { role: "user", text: userText }]);
    setInput("");
    setLoading(true);

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userText, threadId })
    });

    const data = await res.json();
    if (data?.error) {
      setMessages((m) => [...m, { role: "assistant", text: `Error: ${data.error}` }]);
    } else {
      setThreadId(data.threadId);
      setMessages((m) => [...m, { role: "assistant", text: data.text }]);
    }
    setLoading(false);
  }

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 20 }}>
      <h2 style={{ fontSize: 22, marginBottom: 12 }}>Mentor Tester</h2>

      <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 12, height: "75vh", overflowY: "auto" }}>
        {messages.length === 0 ? (
          <div style={{ color: "#666" }}>Ask a question about your TradeHabit analytics…</div>
        ) : (
          messages.map((m, i) => <MessageBubble key={i} role={m.role} text={m.text} />)
        )}
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="e.g., What’s my most common mistake?"
          style={{ flex: 1, padding: 10, borderRadius: 8, border: "1px solid #ccc" }}
        />
        <button onClick={send} disabled={loading} style={{ padding: "10px 14px", borderRadius: 8 }}>
          {loading ? "Thinking…" : "Send"}
        </button>
      </div>
    </div>
  );
}