import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav style={{ padding: "10px", background: "#eee" }}>
      <Link to="/">Home</Link> |{" "}
      <Link to="/insights">Insights</Link> |{" "}
      <Link to="/models">Models</Link> |{" "}
      <Link to="/workflows">Workflows</Link>
    </nav>
  );
}
