// frontend/src/App.jsx
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Home from "./pages/Home.jsx";
import Chat from "./pages/Chat.jsx";
import RunDetail from "./pages/RunDetail.jsx";
import Workflows from "./pages/Workflows.jsx";
import Models from "./pages/Models.jsx";
import Insights from "./pages/Insights.jsx";
import Automations from "./pages/Automations.jsx";
import AppGen from "./pages/AppGen.jsx";
import Apps from "./pages/Apps.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#0b1220] text-white">
        <Navbar />
        <div className="max-w-5xl mx-auto p-4">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/runs/:runId" element={<RunDetail />} />
            <Route path="/workflows" element={<Workflows />} />
            <Route path="/models" element={<Models />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="/automations" element={<Automations />} />
            <Route path="/appgen" element={<AppGen />} />
            <Route path="/apps" element={<Apps />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
