import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

// الصفحات العامة
import LandingPage from "./pages/LandingPage";
import Login from "./pages/Login";
import Register from "./pages/Register";

// Layout
import MainLayout from "./layouts/MainLayout";

// Pages
import Dashboard from "./pages/Dashboard";
import Social from "./pages/Social";
import Profile from "./pages/student/Profile";
import Notifications from "./pages/Notifications";

// Private Route
const PrivateRoute = ({ children, allowedType }) => {
  const token = localStorage.getItem("access_token");
  const userType = localStorage.getItem("user_type");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (allowedType && userType !== allowedType) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <Routes>

        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/student/profile" element={<Navigate to="/profile" replace />} />
        <Route path="/student/social" element={<Navigate to="/social" replace />} />
        <Route path="/student/dashboard" element={<Navigate to="/dashboard" replace />} />

        {/* Main App Layout */}
        <Route
          path="/"
          element={
            <PrivateRoute allowedType="student">
              <MainLayout />
            </PrivateRoute>
          }
        >
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="social" element={<Social />} />
          <Route path="profile" element={<Profile />} />
          <Route path="notifications" element={<Notifications />} />
        </Route>

      </Routes>
    </Router>
  );
}

export default App;
