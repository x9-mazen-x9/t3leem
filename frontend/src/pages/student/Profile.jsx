// src/pages/Student/Profile.jsx
import React, { useEffect, useMemo, useState } from 'react';
import api from '../../api';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [profileError, setProfileError] = useState('');
  const [posts, setPosts] = useState([]);
  const [followingList, setFollowingList] = useState([]);
  const [showFollowing, setShowFollowing] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get('/me/student/');
        setProfile(res.data);
        setProfileError('');
      } catch (err) {
        setProfileError('تعذر تحميل بيانات البروفايل. تأكد من تسجيل الدخول كطالب.');
      }
    };
    fetchProfile();
  }, []);

  useEffect(() => {
    const loadPosts = async () => {
      const res = await api.get('/posts/');
      setPosts(res.data.results || res.data || []);
    };
    loadPosts();
  }, []);

  if (!profile && !profileError) return <div>جاري التحميل...</div>;

  if (!profile && profileError) {
    return (
      <div className="glass-card p-6" dir="rtl" style={{ textAlign: "center", color: "var(--text-secondary)" }}>
        {profileError}
      </div>
    );
  }

  const displayName = profile.name || profile.email || '';
  const userPosts = useMemo(() => {
    return posts.filter(p => p.author_name === displayName || p.author_name === profile.email);
  }, [posts, displayName, profile]);

  return (
    <div dir="rtl">
      <div className="glass-card p-0 mb-6" style={{ overflow: "hidden" }}>
        <div style={{ height: 140, background: "var(--primary-gradient)" }}></div>
        <div style={{ padding: "24px" }}>
          <div style={{ display: "flex", gap: "16px", alignItems: "center", marginTop: "-50px" }}>
            <div style={{ width: 100, height: 100, borderRadius: "50%", background: "var(--glass-bg)", border: "4px solid white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "32px", fontWeight: 800 }}>
              {displayName.charAt(0)}
            </div>
            <div>
              <div style={{ fontSize: "24px", fontWeight: 800 }}>{displayName}</div>
              <div style={{ color: "var(--text-secondary)" }}>طالب</div>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "12px", marginTop: "24px" }}>
            <div className="glass-card p-4" style={{ textAlign: "center" }}>
              <div className="text-2xl font-extrabold">{profile.stats?.posts ?? 0}</div>
              <div style={{ color: "var(--text-secondary)" }}>Posts</div>
            </div>
            <button
              className="glass-card p-4"
              style={{ textAlign: "center" }}
              onClick={async () => {
                const res = await api.get('/teachers/following/');
                setFollowingList(res.data || []);
                setShowFollowing(true);
              }}
            >
              <div className="text-2xl font-extrabold">{profile.stats?.following ?? 0}</div>
              <div style={{ color: "var(--text-secondary)" }}>Following</div>
            </button>
            <div className="glass-card p-4" style={{ textAlign: "center" }}>
              <div className="text-2xl font-extrabold">{profile.stats?.likes ?? 0}</div>
              <div style={{ color: "var(--text-secondary)" }}>Likes</div>
            </div>
          </div>
        </div>
      </div>

      <div className="glass-card p-6 mb-6">
        <h3 className="text-xl font-bold mb-4">منشوراتي</h3>
        {userPosts.length === 0 && (
          <div style={{ textAlign: "center", color: "var(--text-secondary)" }}>لا توجد منشورات بعد</div>
        )}
        {userPosts.map((post) => (
          <div key={post.id} className="glass-card p-4 mb-4">
            <h4 className="font-bold mb-2">{post.title || "منشور"}</h4>
            <p>{post.content}</p>
          </div>
        ))}
      </div>

      {showFollowing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,0.5)" }}>
          <div className="glass-card p-6" style={{ width: "100%", maxWidth: 520 }}>
            <div className="flex items-center justify-between mb-4">
              <div className="text-xl font-bold">المدرسون الذين أتابعهم</div>
              <button className="btn" onClick={() => setShowFollowing(false)}>إغلاق</button>
            </div>
            <div style={{ maxHeight: 380, overflowY: "auto" }}>
              {(followingList || []).map(t => (
                <div key={t.id} className="glass-card p-3 mb-3" style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                  <div style={{ width: 40, height: 40, borderRadius: "50%", background: "var(--primary-gradient)", color: "white", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    {t.full_name?.charAt(0)}
                  </div>
                  <div>
                    <div className="font-bold">{t.full_name}</div>
                    <div style={{ color: "var(--text-secondary)", fontSize: 12 }}>متابعين: {t.follower_count}</div>
                  </div>
                </div>
              ))}
              {(!followingList || followingList.length === 0) && (
                <div style={{ textAlign: "center", color: "var(--text-secondary)" }}>لا توجد متابعات</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
