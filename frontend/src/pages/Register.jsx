// src/pages/RegisterPage.jsx
import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import ThemeSwitch from "../components/ThemeSwitch";
import BackButton from "../components/BackButton";
import api from "../api";

const RegisterPage = () => {
  const navigate = useNavigate();
  const [isDark, setIsDark] = useState(false);
  const [isTeacher, setIsTeacher] = useState(false);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    fullName: "",
    phone: "",
    guardianPhone: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  // تحميل الثيم
  useEffect(() => {
    const isDarkMode = document.body.classList.contains("dark-mode");
    setIsDark(isDarkMode);
  }, []);

  // تغيير الثيم
  const handleThemeChange = () => {
    document.body.classList.toggle("dark-mode");
    setIsDark(!isDark);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // 1. التحقق من تطابق كلمة المرور
    if (formData.password !== formData.confirmPassword) {
      alert("كلمتا المرور غير متطابقتين");
      return;
    }

    // 2. التحقق من رقم ولي الأمر للطالب
    if (!isTeacher && !formData.guardianPhone) {
      alert("رقم ولي الأمر مطلوب للطلاب");
      return;
    }

    // 3. تجهيز البيانات (Mapping)
    // الباك اند يتوقع first_name و last_name منفصلين
    const nameParts = formData.fullName.trim().split(/\s+/);
    const firstName = nameParts[0];
    const lastName = nameParts.slice(1).join(" ") || " "; // لو كتب اسم واحد بس

    const payload = {
      first_name: firstName,
      last_name: lastName,
      email: formData.email,
      phone: formData.phone,
      password: formData.password,
      confirm_password: formData.confirmPassword,
      user_type: isTeacher ? "teacher" : "student",
      parent_phone: isTeacher ? "" : formData.guardianPhone,
    };

    // 4. إرسال الطلب للباك اند
    try {
      setLoading(true);
      const res = await api.post("/auth/register/", payload);
      
      alert("تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.");
      navigate("/login"); // تحويل المستخدم لصفحة الدخول

    } catch (err) {
      console.error(err.response?.data);
      // محاولة عرض رسالة الخطأ بشكل واضح
      const errorMsg = err.response?.data?.detail 
        || JSON.stringify(err.response?.data) 
        || "حدث خطأ أثناء التسجيل";
      alert(`خطأ: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div dir="rtl">
      <div className="bg-blob blob-1"></div>
      <div className="bg-blob blob-2"></div>

      <div className="register-wrapper">
        <div className="register-card glass-card">

          {/* Top Actions */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "30px",
            }}
          >
            <BackButton />

            <ThemeSwitch
              isChecked={isDark}
              onChange={handleThemeChange}
            />
          </div>

          <div style={{ textAlign: "center", marginBottom: "35px" }}>
            <h1 className="logo">MAJMA</h1>
            <p style={{ color: "var(--text-secondary)", marginTop: "5px" }}>
              أنشئ حسابك وابدأ الرحلة
            </p>
          </div>

          {/* Toggle */}
          <div
            className={`user-type-toggle ${
              isTeacher ? "teacher-active" : ""
            }`}
            onClick={() => setIsTeacher(!isTeacher)}
          >
            <div className="toggle-bg"></div>
            <div className={`toggle-option ${!isTeacher ? "active" : ""}`}>
              طالب
            </div>
            <div className={`toggle-option ${isTeacher ? "active" : ""}`}>
              مدرس
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>الاسم بالكامل</label>
              <input
                type="text"
                name="fullName"
                required
                onChange={handleChange}
                placeholder="مثال: محمد أحمد علي"
              />
            </div>

            <div className="form-group">
              <label>رقم الهاتف</label>
              <input
                type="tel"
                name="phone"
                required
                onChange={handleChange}
                placeholder="01xxxxxxxxx"
              />
            </div>

            {/* حقل ولي الأمر يظهر للطالب فقط */}
            {!isTeacher && (
              <div className="form-group">
                <label>رقم هاتف ولي الأمر</label>
                <input
                  type="tel"
                  name="guardianPhone"
                  required
                  onChange={handleChange}
                  placeholder="رقم ولي الأمر"
                />
              </div>
            )}

            <div className="form-group">
              <label>البريد الإلكتروني</label>
              <input
                type="email"
                name="email"
                required
                onChange={handleChange}
                placeholder="example@email.com"
              />
            </div>

            <div className="form-group">
              <label>كلمة المرور</label>
              <input
                type="password"
                name="password"
                required
                onChange={handleChange}
                placeholder="********"
              />
            </div>

            <div className="form-group">
              <label>تأكيد كلمة المرور</label>
              <input
                type="password"
                name="confirmPassword"
                required
                onChange={handleChange}
                placeholder="********"
              />
            </div>

            <button 
              type="submit" 
              className="submit-btn" 
              disabled={loading} // تعطيل الزر أثناء التحميل
            >
              {loading ? "جاري التسجيل..." : "إنشاء الحساب"}
            </button>
          </form>

          <div className="login-link">
            لديك حساب بالفعل؟{" "}
            <Link to="/login">سجل دخول</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;