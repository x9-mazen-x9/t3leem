// src/layouts/StudentLayout.jsx
import React, { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";

const StudentLayout = () => {
  const location = useLocation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // دالة لتحديد اللينك النشط
  const isActive = (path) =>
    location.pathname === path ? "nav-item active" : "nav-item";

  return (
    <div className="dashboard-container" dir="rtl">
      {/* Sidebar */}
      <aside className={`sidebar ${isSidebarOpen ? "open" : ""}`}>
        <div className="sidebar-header">
          <h2 className="logo" style={{ fontSize: "1.5rem" }}>
            MAJMA
          </h2>
          <p className="text-sm opacity-70">لوحة الطالب</p>
        </div>

        <nav className="sidebar-nav">
          <Link
            to="/student/dashboard"
            className={isActive("/student/dashboard")}
          >
            <i className="fas fa-home"></i> الرئيسية
          </Link>
          <Link to="/student/courses" className={isActive("/student/courses")}>
            <i className="fas fa-book"></i> كورساتي
          </Link>
          <Link to="/student/social" className={isActive("/student/social")}>
            <i className="fas fa-users"></i> السوشيال
          </Link>
          <Link to="/student/profile" className={isActive("/student/profile")}>
            <i className="fas fa-user"></i> بروفايلي
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header
          className="dashboard-header glass-card"
          style={{
            borderRadius: "0",
            padding: "15px 30px",
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <button
            className="menu-toggle"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          >
            <i className="fas fa-bars"></i>
          </button>
          <div style={{ display: "flex", gap: "15px", alignItems: "center" }}>
            <span className="text-sm font-bold">أهلاً بيك 👋</span>
          </div>
        </header>

        {/* Page Content */}
        <div className="content-area" style={{ padding: "30px" }}>
          <Outlet /> {/* هنا هتظهر محتويات الصفحات */}
        </div>
      </main>
    </div>
  );
};

export default StudentLayout;
