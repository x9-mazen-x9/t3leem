import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Sun, Moon, ArrowRight } from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import api from "../api";

const RegisterPage = () => {
  const navigate = useNavigate();
  const [isTeacher, setIsTeacher] = useState(false);
  const [loading, setLoading] = useState(false);
  const { theme, toggleTheme } = useTheme();

  const [formData, setFormData] = useState({
    fullName: "",
    phone: "",
    guardianPhone: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

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
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100" dir="rtl">
      <div className="relative">
        <div className="pointer-events-none absolute -top-24 right-0 h-72 w-72 rounded-full bg-indigo-500/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-24 left-0 h-72 w-72 rounded-full bg-purple-500/20 blur-3xl" />
      </div>

      <div className="mx-auto flex min-h-screen max-w-2xl items-center px-4">
        <div className="w-full rounded-2xl border border-white/10 bg-white/70 p-8 shadow-xl backdrop-blur dark:bg-slate-900/60">
          <div className="mb-6 flex items-center justify-between">
            <Link to="/" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-900 dark:text-slate-400">
              <ArrowRight size={18} /> الرجوع
            </Link>
            <button
              onClick={toggleTheme}
              className="rounded-xl border border-white/10 p-2 hover:bg-black/5 dark:hover:bg-white/10"
            >
              {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>

          <div className="mb-6 text-center">
            <h1 className="text-3xl font-extrabold bg-gradient-to-r from-indigo-500 to-purple-500 bg-clip-text text-transparent">
              MAJMA
            </h1>
            <p className="mt-2 text-slate-500 dark:text-slate-400">أنشئ حسابك وابدأ الرحلة</p>
          </div>

          <div className="mb-6 grid grid-cols-2 rounded-2xl border border-white/10 bg-slate-100 p-1 dark:bg-slate-800">
            <button
              type="button"
              onClick={() => setIsTeacher(false)}
              className={`rounded-xl py-2 text-sm font-bold ${!isTeacher ? "bg-indigo-500 text-white" : "text-slate-500 dark:text-slate-300"}`}
            >
              طالب
            </button>
            <button
              type="button"
              onClick={() => setIsTeacher(true)}
              className={`rounded-xl py-2 text-sm font-bold ${isTeacher ? "bg-indigo-500 text-white" : "text-slate-500 dark:text-slate-300"}`}
            >
              مدرس
            </button>
          </div>

          <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
            <input
              type="text"
              name="fullName"
              required
              onChange={handleChange}
              placeholder="الاسم بالكامل"
              className="md:col-span-2 w-full rounded-xl border border-white/10 bg-slate-100 px-4 py-3 outline-none dark:bg-slate-800"
            />
            <input
              type="tel"
              name="phone"
              required
              onChange={handleChange}
              placeholder="رقم الهاتف"
              className="w-full rounded-xl border border-white/10 bg-slate-100 px-4 py-3 outline-none dark:bg-slate-800"
            />
            {!isTeacher && (
              <input
                type="tel"
                name="guardianPhone"
                required
                onChange={handleChange}
                placeholder="رقم ولي الأمر"
                className="w-full rounded-xl border border-white/10 bg-slate-100 px-4 py-3 outline-none dark:bg-slate-800"
              />
            )}
            <input
              type="email"
              name="email"
              required
              onChange={handleChange}
              placeholder="البريد الإلكتروني"
              className="md:col-span-2 w-full rounded-xl border border-white/10 bg-slate-100 px-4 py-3 outline-none dark:bg-slate-800"
            />
            <input
              type="password"
              name="password"
              required
              onChange={handleChange}
              placeholder="كلمة المرور"
              className="w-full rounded-xl border border-white/10 bg-slate-100 px-4 py-3 outline-none dark:bg-slate-800"
            />
            <input
              type="password"
              name="confirmPassword"
              required
              onChange={handleChange}
              placeholder="تأكيد كلمة المرور"
              className="w-full rounded-xl border border-white/10 bg-slate-100 px-4 py-3 outline-none dark:bg-slate-800"
            />

            <button
              type="submit"
              className="md:col-span-2 rounded-xl bg-indigo-500 py-3 font-bold text-white hover:bg-indigo-600 disabled:opacity-70"
              disabled={loading}
            >
              {loading ? "جاري التسجيل..." : "إنشاء الحساب"}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
            لديك حساب بالفعل؟ <Link to="/login" className="font-bold text-indigo-500">سجل دخول</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
