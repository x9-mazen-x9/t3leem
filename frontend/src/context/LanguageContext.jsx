import React, { createContext, useContext, useState, useEffect } from 'react';

const translations = {
  en: {
    nav_home: 'Home',
    nav_login: 'Login',
    nav_register: 'Register',
    nav_dashboard: 'Dashboard',
    nav_logout: 'Logout',
    hero_title: 'Master Your Future with Ta3leem',
    hero_subtitle: 'The next-generation learning platform designed for the modern world.',
    cta_login: 'Login Now',
    cta_register: 'Get Started',
    feat_1_title: 'Interactive Learning',
    feat_1_desc: 'Engage with content like never before.',
    feat_2_title: 'Real-time Analytics',
    feat_2_desc: 'Track your progress instantly.',
    feat_3_title: 'Global Community',
    feat_3_desc: 'Connect with learners worldwide.',
    login_title: 'Welcome Back',
    email_label: 'Email Address',
    password_label: 'Password',
    login_btn: 'Sign In',
    register_title: 'Create Account',
    register_btn: 'Sign Up',
    dash_welcome: 'Welcome back',
    dash_stats_courses: 'Courses',
    dash_stats_hours: 'Hours Learned',
  },
  ar: {
    nav_home: 'الرئيسية',
    nav_login: 'تسجيل الدخول',
    nav_register: 'إنشاء حساب',
    nav_dashboard: 'لوحة التحكم',
    nav_logout: 'تسجيل الخروج',
    hero_title: 'أتقن مستقبلك مع تعليم',
    hero_subtitle: 'منصة تعليمية من الجيل القادم، مصممة للعالم الحديث.',
    cta_login: 'دخول',
    cta_register: 'ابدأ الآن',
    feat_1_title: 'تعليم تفاعلي',
    feat_1_desc: 'تفاعل مع المحتوى بشكل لم يسبق له مثيل.',
    feat_2_title: 'تحليلات فورية',
    feat_2_desc: 'تتبع تقدمك لحظة بلحظة.',
    feat_3_title: 'مجتمع عالمي',
    feat_3_desc: 'تواصل مع المتعلمين حول العالم.',
    login_title: 'مرحباً بعودتك',
    email_label: 'البريد الإلكتروني',
    password_label: 'كلمة المرور',
    login_btn: 'تسجيل الدخول',
    register_title: 'إنشاء حساب جديد',
    register_btn: 'إنشاء الحساب',
    dash_welcome: 'مرحباً بعودتك',
    dash_stats_courses: 'الدورات',
    dash_stats_hours: 'ساعات التعلم',
  }
};

const LanguageContext = createContext(null);

export const LanguageProvider = ({ children }) => {
  const [lang, setLang] = useState(() => localStorage.getItem('lang') || 'en');

  useEffect(() => {
    const root = window.document.documentElement;
    root.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
    root.setAttribute('lang', lang);
    localStorage.setItem('lang', lang);
  }, [lang]);

  const toggleLang = () => {
    setLang((prev) => (prev === 'en' ? 'ar' : 'en'));
  };

  const t = translations[lang];

  return (
    <LanguageContext.Provider value={{ lang, toggleLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);