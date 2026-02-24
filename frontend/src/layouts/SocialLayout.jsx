import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';

const SocialLayout = () => {
  const location = useLocation();
  
  return (
    <div className="social-app-container" dir="rtl">
      {/* Navbar بسيط أعلى الصفحة */}
      <header className="social-header glass-card" style={{ borderRadius: 0, position: 'sticky', top: 0, zIndex: 100 }}>
        <div className="nav-content" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 50px' }}>
          
          {/* الشمال: اللوجو */}
          <Link to="/student/social" className="logo" style={{ fontSize: '1.5rem' }}>
            MAJMA
          </Link>

          {/* الوسط: بحث */}
          <div style={{ flex: 1, margin: '0 40px' }}>
            <input 
              type="text" 
              placeholder="ابحث عن مدرس أو كورس..." 
              className="input-field" 
              style={{ background: 'var(--input-bg)', height: '40px', marginBottom: 0 }}
            />
          </div>

          {/* اليمين: الأيقونات */}
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <Link to="/student/social" className="icon-btn-nav">
                <i className="fas fa-home"></i>
            </Link>
            <Link to="/student/social?tab=following" className="icon-btn-nav">
                <i className="fas fa-user-friends"></i> {/* أيقونة المتابعة */}
            </Link>
            <Link to="/notifications" className="icon-btn-nav">
                <i className="fas fa-bell"></i>
            </Link>
            <Link to="/student/profile" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <div style={{ width: '35px', height: '35px', borderRadius: '50%', background: 'var(--primary-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
                    <i className="fas fa-user"></i>
                </div>
            </Link>
          </div>
        </div>
      </header>

      {/* المحتوى */}
      <main style={{ background: 'var(--bg-color)', minHeight: '100vh' }}>
        <Outlet />
      </main>
    </div>
  );
};

export default SocialLayout;