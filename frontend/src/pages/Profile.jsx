import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

const Profile = () => {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    api.get('/me/student/')
      .then(res => setProfile(res.data))
      .catch(err => console.error(err));
  }, []);

  if (!profile) return <div className="text-center p-10">جاري التحميل...</div>;

  return (
    <div className="profile-page" style={{ padding: '50px', display: 'flex', justifyContent: 'center' }}>
      <div className="glass-card" style={{ width: '100%', maxWidth: '800px', padding: 0, overflow: 'hidden' }}>
        
        {/* الغلاف والصورة */}
        <div style={{ height: '150px', background: 'var(--primary-gradient)', position: 'relative' }}>
          <div style={{ position: 'absolute', bottom: '-50px', right: '30px' }}>
            <div style={{ width: '100px', height: '100px', borderRadius: '50%', border: '4px solid white', background: '#ddd', overflow: 'hidden' }}>
                {/* صورة البروفايل */}
                {profile.image ? 
                    <img src={profile.image} alt="" style={{width:'100%', height:'100%', objectFit:'cover'}} /> :
                    <div style={{width:'100%', height:'100%', background:'var(--glass-bg)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'2rem'}}>
                        <i className="fas fa-user"></i>
                    </div>
                }
            </div>
          </div>
        </div>

        {/* الاسم والبيانات */}
        <div style={{ padding: '60px 30px 30px', textAlign: 'right' }}>
          <h2 className="text-2xl font-bold">{profile.name}</h2>
          <p className="text-gray-400">{profile.email}</p>

          {/* الإحصائيات (نقطة 4) */}
          <div className="grid grid-cols-3 gap-4 my-6 text-center">
            <div className="p-4 bg-white/5 rounded-lg">
                <Link to="/student/following">
                    <h3 className="text-xl font-bold">{profile.stats?.following || 0}</h3>
                    <p className="text-sm text-gray-400">متابَع</p>
                </Link>
            </div>
            <div className="p-4 bg-white/5 rounded-lg">
                <h3 className="text-xl font-bold">{profile.stats?.posts || 0}</h3>
                <p className="text-sm text-gray-400">بوستات</p>
            </div>
            <div className="p-4 bg-white/5 rounded-lg">
                <h3 className="text-xl font-bold">{profile.stats?.likes || 0}</h3>
                <p className="text-sm text-gray-400">إعجاب</p>
            </div>
          </div>

          {/* البيانات الحساسة (نقطة 2 - تظهر لصاحبها بس) */}
          <div className="mt-8 border-t pt-6 border-white/10 space-y-3">
            <div className="flex justify-between">
                <span className="text-gray-400">الرقم التسلسلي:</span>
                <span className="font-mono font-bold text-indigo-400">{profile.serial_number}</span>
            </div>
            <div className="flex justify-between">
                <span className="text-gray-400">رقم الهاتف:</span>
                <span>{profile.phone}</span>
            </div>
            <div className="flex justify-between">
                <span className="text-gray-400">رقم ولي الأمر:</span>
                <span>{profile.parent_phone}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;