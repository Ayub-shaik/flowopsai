import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Insights from "./pages/Insights.jsx";
import Models from "./pages/Models.jsx";
import Workflows from "./pages/Workflows.jsx";
import Navbar from "./components/Navbar.jsx";

export default function App() {
  return (
    <>
      <Navbar />
      <main style={{ padding: 16 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/models" element={<Models />} />
          <Route path="/workflows" element={<Workflows />} />
        </Routes>
      </main>
    </>
  );
}
