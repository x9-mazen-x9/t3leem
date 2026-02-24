// src/pages/LandingPage.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import ThemeSwitch from "../components/ThemeSwitch"; // 1. استدعاء المكون الجديد
import Logo from "../components/LogoTemp";

const LandingPage = () => {
  // 2. حالة الثيم (State)
  const [isDark, setIsDark] = useState(false);

  // 3. التحقق من الثيم عند تحميل الصفحة
  useEffect(() => {
    const isDarkMode = document.body.classList.contains("dark-mode");
    setIsDark(isDarkMode);

    const header = document.getElementById("main-header");
    const handleScroll = () => {
      if (window.scrollY > 50) header.classList.add("scrolled");
      else header.classList.remove("scrolled");
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // 4. فانكشن التبديل
  const handleThemeChange = () => {
    document.body.classList.toggle("dark-mode");
    setIsDark(!isDark);
  };

  return (
    <div dir="rtl">
      <div className="bg-blob blob-1"></div>
      <div className="bg-blob blob-2"></div>

      <header id="main-header">
        <div className="nav-content">
          <Link to="/">
            <Logo variant="icon" isDark={isDark} className="nav-logo" />
          </Link>

          <nav>
            <ul className="nav-links">
              <li>
                <a href="#features">المميزات</a>
              </li>
              <li>
                <a href="#social">المجتمع</a>
              </li>
            </ul>
          </nav>

          <div style={{ display: "flex", gap: "15px", alignItems: "center" }}>
            {/* 5. استخدام الـ Switch الجديد هنا */}
            <ThemeSwitch isChecked={isDark} onChange={handleThemeChange} />

            <Link to="/login" className="btn btn-primary">
              ابدأ الآن
            </Link>
          </div>
        </div>
      </header>
      {/* قسم الهيرو */}
      <section className="hero">
        <div className="hero-text">
          <h1>
            مجتمعك التعليمي في مكان واحد
            <br />
            <span
              style={{
                background: "var(--primary-gradient)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              تعلم، تفاعل، وتطور
            </span>
          </h1>
          <p>
            منصة تجمع بين قوة أنظمة إدارة التعلم LMS وبين حيوية الشبكات
            الاجتماعية. للمدرسين وللطلاب، تجربة تعليمية ذكية وآمنة.
          </p>
          <div style={{ display: "flex", gap: "15px" }}>
            <Link to="/register" className="btn btn-primary">
              انضم كمدرس
            </Link>
            <Link to="/register" className="btn btn-outline">
              انضم كطالب
            </Link>
          </div>
        </div>

        <div className="hero-image">
          {/* صورة أو شكل توضيحي */}
          <div
            className="glass-card"
            style={{
              width: "400px",
              height: "300px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Logo variant="full" isDark={isDark} className="hero-logo" />
          </div>
        </div>
      </section>

      {/* قسم المميزات */}
      <section
        id="features"
        style={{ padding: "80px 20px", maxWidth: "1200px", margin: "0 auto" }}
      >
        <div style={{ textAlign: "center", marginBottom: "60px" }}>
          <h2 style={{ fontSize: "2.5rem" }}>لماذا مجمع؟</h2>
          <p style={{ color: "var(--text-secondary)", marginTop: "10px" }}>
            نقدم لك ميزات لا مثيل لها
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            gap: "30px",
          }}
        >
          {/* ميزة 1 */}
          <div
            className="glass-card"
            style={{ padding: "40px", textAlign: "center" }}
          >
            <div
              style={{
                width: "70px",
                height: "70px",
                background: "var(--primary-gradient)",
                borderRadius: "20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 20px",
                color: "white",
                fontSize: "2rem",
              }}
            >
              <i className="fas fa-layer-group"></i>
            </div>
            <h3 style={{ fontSize: "1.4rem", marginBottom: "10px" }}>
              هيكل كورسات متكامل
            </h3>
            <p style={{ color: "var(--text-secondary)", lineHeight: 1.6 }}>
              نظام دعم الكورسات، الوحدات، والدروس مع إمكانية رفع الملفات بسهولة.
            </p>
          </div>

          {/* ميزة 2 */}
          <div
            className="glass-card"
            style={{ padding: "40px", textAlign: "center" }}
          >
            <div
              style={{
                width: "70px",
                height: "70px",
                background: "var(--primary-gradient)",
                borderRadius: "20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 20px",
                color: "white",
                fontSize: "2rem",
              }}
            >
              <i className="fas fa-shield-alt"></i>
            </div>
            <h3 style={{ fontSize: "1.4rem", marginBottom: "10px" }}>
              أمان عالي (Bunny Stream)
            </h3>
            <p style={{ color: "var(--text-secondary)", lineHeight: 1.6 }}>
              حماية محتواك الفيديوي من التحميل غير المصرح به بأعلى جودة.
            </p>
          </div>

          {/* ميزة 3 */}
          <div
            className="glass-card"
            style={{ padding: "40px", textAlign: "center" }}
          >
            <div
              style={{
                width: "70px",
                height: "70px",
                background: "var(--primary-gradient)",
                borderRadius: "20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 20px",
                color: "white",
                fontSize: "2rem",
              }}
            >
              <i className="fas fa-users"></i>
            </div>
            <h3 style={{ fontSize: "1.4rem", marginBottom: "10px" }}>
              تفاعل اجتماعي
            </h3>
            <p style={{ color: "var(--text-secondary)", lineHeight: 1.6 }}>
              بيئة تعليمية تجمع الطلاب والمدرسين في مجتمع تفاعلي آمن.
            </p>
          </div>
        </div>
      </section>

      {/* الفوتر */}
      <footer
        style={{
          marginTop: "50px",
          padding: "30px",
          textAlign: "center",
          borderTop: "1px solid var(--glass-border)",
        }}
      >
        <p style={{ color: "var(--text-secondary)" }}>
          © 2024 مجمع MAJMA. جميع الحقوق محفوظة.
        </p>
      </footer>
    </div>
  );
};

export default LandingPage;
