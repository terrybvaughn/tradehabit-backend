import React from "react";

export default function MessageBubble({ role, text }: { role: "user" | "assistant"; text: string }) {
  const isUser = role === "user";
  return (
    <div style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", margin: "8px 0" }}>
      <div
        style={{
          maxWidth: 720,
          padding: 12,
          borderRadius: 12,
          background: isUser ? "#1a73e8" : "#f1f3f4",
          color: isUser ? "#fff" : "#111",
          whiteSpace: "pre-wrap"
        }}
      >
        {text}
      </div>
    </div>
  );
}