import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Insights from "./pages/Insights";
import Models from "./pages/Models";
import Workflows from "./pages/Workflows";

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/models" element={<Models />} />
        <Route path="/workflows" element={<Workflows />} />
      </Routes>
    </Router>
  );
}

export default App;
