import React, { useEffect, useState } from "react";
import api from "../api";

const Notifications = () => {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.get("/notifications/");
      setList(res.data.results || res.data || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const markAsRead = async (id) => {
    await api.post(`/notifications/${id}/mark_as_read/`);
    load();
  };

  const markAll = async () => {
    await api.post(`/notifications/mark_all_as_read/`);
    load();
  };

  return (
    <div className="max-w-2xl mx-auto p-6" dir="rtl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">الإشعارات</h2>
        <button className="btn btn-primary" onClick={markAll}>
          تعليم الكل كمقروء
        </button>
      </div>
      <div className="space-y-3">
        {loading && <div>جارِ التحميل...</div>}
        {!loading &&
          (list || []).map((n) => (
            <div key={n.id} className="glass-card p-4 flex items-start justify-between">
              <div>
                <div className="font-bold">{n.title}</div>
                <div style={{ color: "var(--text-secondary)" }}>{n.message}</div>
              </div>
              {!n.is_read && (
                <button className="btn" onClick={() => markAsRead(n.id)}>
                  تمت القراءة
                </button>
              )}
            </div>
          ))}
        {!loading && list.length === 0 && (
          <div className="glass-card p-6 text-center" style={{ color: "var(--text-secondary)" }}>
            لا توجد إشعارات
          </div>
        )}
      </div>
    </div>
  );
};

export default Notifications;
