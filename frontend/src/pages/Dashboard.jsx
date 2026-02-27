import React, { useEffect, useState } from "react";
import { Heart, Users, MessageSquare, Plus, Newspaper } from "lucide-react";
import api from "../api";

const Dashboard = () => {
  const [stats, setStats] = useState({ posts: 0, followers: 0, likes: 0 });

  useEffect(() => {
    const load = async () => {
      try {
        const me = await api.get("/me/student/");
        setStats({
          posts: me.data?.stats?.posts || 0,
          followers: me.data?.stats?.following || 0,
          likes: me.data?.stats?.likes || 0,
        });
      } catch {}
    };
    load();
  }, []);

  return (
    <div dir="rtl">
      <div className="glass-card p-6 mb-6">
        <h2 className="text-2xl font-bold mb-4">لوحة التحكم</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
          <div className="glass-card p-4" style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <div style={{ width: 44, height: 44, borderRadius: 12, background: "var(--primary-gradient)", display: "flex", alignItems: "center", justifyContent: "center", color: "white" }}>
              <Newspaper size={20} />
            </div>
            <div>
              <div className="text-xl font-bold">{stats.posts}</div>
              <div style={{ color: "var(--text-secondary)" }}>عدد المنشورات</div>
            </div>
          </div>
          <div className="glass-card p-4" style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <div style={{ width: 44, height: 44, borderRadius: 12, background: "var(--primary-gradient)", display: "flex", alignItems: "center", justifyContent: "center", color: "white" }}>
              <Users size={20} />
            </div>
            <div>
              <div className="text-xl font-bold">{stats.followers}</div>
              <div style={{ color: "var(--text-secondary)" }}>عدد المتابَعين</div>
            </div>
          </div>
          <div className="glass-card p-4" style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <div style={{ width: 44, height: 44, borderRadius: 12, background: "var(--primary-gradient)", display: "flex", alignItems: "center", justifyContent: "center", color: "white" }}>
              <Heart size={20} />
            </div>
            <div>
              <div className="text-xl font-bold">{stats.likes}</div>
              <div style={{ color: "var(--text-secondary)" }}>عدد الإعجابات</div>
            </div>
          </div>
        </div>
      </div>

      <div className="glass-card p-6">
        <h3 className="text-xl font-bold mb-4">إجراءات سريعة</h3>
        <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
          <a href="/social" className="btn btn-primary">الذهاب للسوشيال</a>
          <a href="/social" className="btn btn-outline" style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
            <Plus size={18} /> إنشاء بوست
          </a>
          <a href="/profile" className="btn btn-outline" style={{ display: "inline-flex", gap: 6, alignItems: "center" }}>
            <MessageSquare size={18} /> إدارة حسابي
          </a>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
