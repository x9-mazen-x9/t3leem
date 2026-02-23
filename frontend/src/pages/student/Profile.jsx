// src/pages/Student/Profile.jsx
import React, { useEffect, useState } from 'react';
import api from '../../api';

const Profile = () => {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get('/me/student/');
        setProfile(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchProfile();
  }, []);

  if (!profile) return <div>جاري التحميل...</div>;

  return (
    <div className="max-w-xl mx-auto">
      <div className="glass-card p-8">
        <div className="text-center mb-8">
          <div className="w-24 h-24 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 mx-auto flex items-center justify-center text-white text-3xl font-bold mb-4">
            {profile.first_name?.charAt(0)}
          </div>
          <h2 className="text-2xl font-bold">{profile.first_name} {profile.last_name}</h2>
          <p className="text-gray-400">{profile.email}</p>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between p-3 bg-white/5 rounded-lg">
            <span className="font-bold">رقم الهاتف:</span>
            <span>{profile.phone}</span>
          </div>
          
          {/* نقطة 21: الرقم التسلسلي */}
          <div className="flex justify-between p-3 bg-white/5 rounded-lg">
            <span className="font-bold">الرقم التسلسلي:</span>
            <span className="text-indigo-400 font-mono">{profile.serial_number}</span>
          </div>

          {/* نقطة 1: رقم ولي الأمر */}
          <div className="flex justify-between p-3 bg-white/5 rounded-lg">
            <span className="font-bold">رقم ولي الأمر:</span>
            <span>{profile.parent_phone}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;