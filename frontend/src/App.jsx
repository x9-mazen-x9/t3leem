import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

// الصفحات العامة
import LandingPage from "./pages/LandingPage";
import Login from "./pages/Login";
import Register from "./pages/Register";

// Layouts
import StudentLayout from "./layouts/StudentLayout";
import SocialLayout from "./layouts/SocialLayout";

// صفحات الطالب
import StudentDashboard from "./pages/student/StudentDashboard";
import Courses from "./pages/student/Courses";
import CourseDetail from "./pages/student/CourseDetail";
import LessonPage from "./pages/student/LessonPage";
import Profile from "./pages/student/Profile";
import Social from "./pages/Social";

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

        {/* Student Sidebar Layout */}
        <Route
          path="/student"
          element={
            <PrivateRoute allowedType="student">
              <StudentLayout />
            </PrivateRoute>
          }
        >
          <Route path="dashboard" element={<StudentDashboard />} />
          <Route path="courses" element={<Courses />} />
          <Route path="courses/:id" element={<CourseDetail />} />
          <Route path="lesson/:lessonId" element={<LessonPage />} />
          <Route index element={<Navigate to="dashboard" replace />} />
        </Route>

        {/* Student Top Navbar Layout */}
        <Route
          path="/student"
          element={
            <PrivateRoute allowedType="student">
              <SocialLayout />
            </PrivateRoute>
          }
        >
          <Route path="social" element={<Social />} />
          <Route path="profile" element={<Profile />} />
        </Route>

      </Routes>
    </Router>
  );
}

export default App;