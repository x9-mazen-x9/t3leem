// src/pages/Login.jsx
import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import ThemeSwitch from "../components/ThemeSwitch";
import BackButton from "../components/BackButton";
import api from "../api";

const Login = () => {
  const navigate = useNavigate();
  const [isDark, setIsDark] = useState(false);

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  useEffect(() => {
    const isDarkMode = document.body.classList.contains("dark-mode");
    setIsDark(isDarkMode);
  }, []);

  const handleThemeChange = () => {
    document.body.classList.toggle("dark-mode");
    setIsDark(!isDark);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // 1. أخد التوكن
      const res = await api.post("/auth/login/", formData);
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);

      // 2. معرفة نوع المستخدم
      const userRes = await api.get("/auth/me/");
      const userType = userRes.data.user_type;
      localStorage.setItem("user_type", userType);

      // 3. التوجيه بناءً على النوع (تعديل هنا)
      navigate("/dashboard");

    } catch (err) {
      alert("خطأ في البيانات! تأكد من البريد وكلمة المرور.");
    }
  };

  return (
    <div dir="rtl">
      <div className="bg-blob blob-1"></div>
      <div className="bg-blob blob-2"></div>

      <div className="login-wrapper">
        <div className="login-card glass-card">
          <div className="top-actions">
            <BackButton />
            <ThemeSwitch isChecked={isDark} onChange={handleThemeChange} />
          </div>

          <div className="login-logo">
            <h1 className="logo">MAJMA</h1>
            <p>أهلاً بعودتك 👋</p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>البريد الإلكتروني</label>
              <input
                type="email"
                name="email"
                placeholder="example@email.com"
                required
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
              />
            </div>

            <div className="form-group">
              <label>كلمة المرور</label>
              <input
                type="password"
                name="password"
                placeholder="********"
                required
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
              />
            </div>

            <button type="submit" className="submit-btn">
              تسجيل الدخول
            </button>
          </form>

          <div className="login-footer">
            ليس لديك حساب؟{" "}
            <Link to="/register">إنشاء حساب جديد</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
