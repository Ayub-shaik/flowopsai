import React from "react";
import { NavLink } from "react-router-dom";

export default function Navbar() {
  const linkStyle = ({ isActive }) => ({
    padding: "8px 10px",
    borderRadius: 8,
    textDecoration: "none",
    color: "inherit",
    background: isActive ? "rgba(124,156,255,.15)" : "transparent"
  });

  return (
    <nav style={{ display: "flex", gap: 12, padding: 12, borderBottom: "1px solid #eee" }}>
      <NavLink to="/" style={linkStyle} end>Home</NavLink>
      <NavLink to="/chat" style={linkStyle}>Chat</NavLink>
      <NavLink to="/insights" style={linkStyle}>Insights</NavLink>
      <NavLink to="/models" style={linkStyle}>Models</NavLink>
      <NavLink to="/workflows" style={linkStyle}>Workflows</NavLink>
      <NavLink to="/appgen" style={linkStyle}>AppGen</NavLink>
      <NavLink to="/apps" style={linkStyle}>Apps</NavLink>
      <NavLink to="/automations" style={linkStyle}>Automations</NavLink>
    </nav>
  );
}
