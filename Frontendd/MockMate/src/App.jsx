// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Interview from "./pages/interview";
import GeminiInterview from "./pages/gemini-interview";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "sonner";
import "./App.css";
import Profile from "./pages/Profile";
import AllJobs from "./pages/AllJobs";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Toaster richColors position="top-center" />
        <Routes>
          <Route path="/" element={<Layout />}>            <Route index element={<Home />} />
            <Route path="login" element={<Login />} />
            <Route path="register" element={<Register />} />
            <Route path="profile" element={<Profile />} />
            <Route path="/interview/:id" element={<Interview />} />
            <Route path="/gemini-interview/:id" element={<GeminiInterview />} />
            <Route path="/all-jobs" element={<AllJobs />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
