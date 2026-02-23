// src/App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { Outlet } from "react-router-dom";

// 1. الصفحات الأساسية
import LandingPage from "./pages/LandingPage";
import Login from "./pages/Login";
import Register from "./pages/Register";

// 2. اللوك والإدوات الخاصة بالطالب
import StudentLayout from "./layouts/StudentLayout";
import StudentDashboard from "./pages/student/StudentDashboard";
import Courses from "./pages/student/Courses";
import CourseDetail from "./pages/student/CourseDetail";
import LessonPage from "./pages/student/LessonPage";
import Profile from "./pages/student/Profile";

// 3. صفحة السوشيال (المشتركة)
import Social from "./pages/Social"; // تأكد إن الملف ده اتعمل نقله للـ Root كما اتفقنا

// --- مكون حماية الروابط (Private Route) ---
const PrivateRoute = ({ children, allowedType }) => {
  const token = localStorage.getItem("access_token");
  const userType = localStorage.getItem("user_type");

  // لو مفيش توكن -> روح للوجين
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // لو النوع مش مسموح بيه (مثلاً طالب يحاول يدخل dashboard مدرس) -> ارجعه للوجين
  if (allowedType && userType !== allowedType) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* --- الروابط العامة --- */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* --- روابط الطالب (محمية بـ PrivateRoute) --- */}
        {/* لاحظ إن StudentLayout هو الـ Parent، فالـ Sidebar هتظهر في كل الصفحات دي */}
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
          <Route path="social" element={<Social />} />
          <Route path="profile" element={<Profile />} />
          
          /* مسار افتراضي: لما يدخل /student فقط - يحوله للداش بورد */
          <Route index element={<Navigate to="dashboard" replace />} />
        </Route>

        {/* --- روابط المدرس (هنحطها بعدين لما نعمل TeacherLayout) --- */}
        {/* <Route path="/teacher" element={...} /> */}

      </Routes>
    </Router>
  );
}

export default App;