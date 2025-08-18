import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import Chat from "./pages/Chat.jsx";
import Workflows from "./pages/Workflows.jsx";
import Models from "./pages/Models.jsx";
import Insights from "./pages/Insights.jsx";
import RunDetail from "./pages/RunDetail.jsx";

function NavBar() {
  const link = ({ isActive }) =>
    `px-3 py-2 rounded-xl ${isActive ? "bg-white/10" : "hover:bg-white/10"}`;
  return (
    <header className="sticky top-0 z-10 backdrop-blur supports-[backdrop-filter]:bg-bg/70 border-b border-white/10">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
        <div className="font-bold tracking-wide">FlowOpsAI</div>
        <nav className="flex gap-2">
          <NavLink to="/" end className={link}>Chat</NavLink>
          <NavLink to="/workflows" className={link}>Workflows</NavLink>
          <NavLink to="/models" className={link}>Models</NavLink>
          <NavLink to="/insights" className={link}>Insights</NavLink>
        </nav>
        <a className="btn ml-auto" href="https://github.com/Ayub-shaik/flowopsai" target="_blank" rel="noreferrer">GitHub</a>
      </div>
    </header>
  );
}

function Shell({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <NavBar />
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
        {children}
      </main>
      <footer className="text-center text-white/50 py-6 border-t border-white/10">
        © {new Date().getFullYear()} coreai.co.in • FlowOpsAI
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <Shell>
      <Routes>
        <Route path="/" element={<Chat />} />
        <Route path="/workflows" element={<Workflows />} />
        <Route path="/models" element={<Models />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/runs/:id" element={<RunDetail />} />
      </Routes>
    </Shell>
  );
}
