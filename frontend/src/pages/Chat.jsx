import React, { useEffect, useRef, useState } from "react";
import { apiPost } from "../api.js";
import { useNavigate } from "react-router-dom";

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Paste a dataset URL + the task. I’ll create a training run and stream progress." }
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const listRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    listRef.current?.scrollTo(0, listRef.current.scrollHeight);
  }, [messages]);

  async function onSend(e) {
    e?.preventDefault?.();
    if (!input.trim()) return;
    const userMsg = { role: "user", text: input.trim() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setSending(true);
    try {
      const res = await apiPost("/chat/start-train", { prompt: userMsg.text });
      const runId = res.run_id || "demo-001";
      setMessages((m) => [...m, { role: "assistant", text: `Started run #${runId}. Redirecting…` }]);
      navigate(`/runs/${runId}`);
    } catch (err) {
      setMessages((m) => [...m, { role: "assistant", text: `Error: ${err.message}` }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="grid md:grid-cols-3 gap-4">
      <div className="md:col-span-2 card flex flex-col h-[72vh]">
        <div ref={listRef} className="flex-1 overflow-auto space-y-3">
          {messages.map((m, i) => (
            <div key={i} className={`p-3 rounded-xl ${m.role === "user" ? "bg-white/10" : "bg-white/5"}`}>
              <div className="text-xs opacity-60 mb-1">{m.role}</div>
              <div>{m.text}</div>
            </div>
          ))}
        </div>
        <form onSubmit={onSend} className="mt-3 flex gap-2">
          <input className="input" placeholder="Dataset URL + task (e.g., Train BERT on reviews)" value={input} onChange={(e) => setInput(e.target.value)} />
          <button className="btn" disabled={sending}>{sending ? "Sending…" : "Send"}</button>
        </form>
      </div>
      <div className="card">
        <div className="badge mb-3">How it works</div>
        <ol className="list-decimal pl-5 space-y-2 text-white/80">
          <li>Chat your dataset + task</li>
          <li>We create a <b>run</b> and spin up agents</li>
          <li>Watch events & metrics live</li>
          <li>Get artifacts & model card</li>
        </ol>
      </div>
    </div>
  );
}
