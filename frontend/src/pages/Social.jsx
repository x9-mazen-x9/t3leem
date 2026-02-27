import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api';
import { Heart, MessageSquare, Share2 } from "lucide-react";

const Social = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState('');
  const [query, setQuery] = useState('');
  const [imageFiles, setImageFiles] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const [posting, setPosting] = useState(false);
  const [currentUserName, setCurrentUserName] = useState('');
  const [currentUserEmail, setCurrentUserEmail] = useState('');
  const fileInputRef = useRef(null);
  const [searchParams, setSearchParams] = useSearchParams();
  
  // تحديد التبويب النشط
  const activeTab = searchParams.get("tab") || "home";

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const url = activeTab === 'following' ? '/posts/?following=true' : '/posts/';
        const res = await api.get(url);
        setPosts(res.data.results || res.data || []);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [activeTab]);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const res = await api.get('/auth/me/');
        const fullName = `${res.data.first_name || ''} ${res.data.last_name || ''}`.trim();
        setCurrentUserName(fullName);
        setCurrentUserEmail(res.data.email || '');
      } catch {}
    };
    loadUser();
  }, []);

  const filteredPosts = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return posts;
    return posts.filter(p =>
      (p.content || '').toLowerCase().includes(q) ||
      (p.author_name || '').toLowerCase().includes(q)
    );
  }, [posts, query]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!content.trim() && imageFiles.length === 0) {
      alert('اكتب نص أو أرفق صورة');
      return;
    }
    setPosting(true);
    try {
      const formData = new FormData();
      formData.append('title', 'منشور');
      formData.append('content', content);
      imageFiles.forEach((file) => {
        formData.append('images', file);
      });
      const res = await api.post('/posts/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setPosts([res.data, ...posts]);
      setContent('');
      setImageFiles([]);
      setImagePreviews([]);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      const msg = err.response?.data?.detail || 'حصل خطأ أثناء النشر، حاول مرة ثانية';
      alert(msg);
    } finally {
      setPosting(false);
    }
  };

  const handleLike = async (id) => {
    await api.post(`/posts/${id}/like/`);
    setPosts(posts.map(p => p.id === id ? { ...p, likes_count: (p.likes_count || 0) + 1 } : p));
  };

  const handleShare = async (id) => {
    await api.post(`/posts/${id}/share/`);
  };

  const handlePickImage = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;
    if (files.length > 10) {
      alert('الحد الأقصى 10 صور');
    }
    const picked = files.slice(0, 10);
    setImageFiles(picked);
    setImagePreviews(picked.map((f) => URL.createObjectURL(f)));
  };

  useEffect(() => {
    return () => {
      imagePreviews.forEach((u) => URL.revokeObjectURL(u));
    };
  }, [imagePreviews]);

  return (
    <div dir="rtl">
      <div style={{ padding: "30px 0", minHeight: "100vh" }}>
        <div className="container mx-auto" style={{ maxWidth: "700px" }}>
          <div className="glass-card flex mb-6 p-2 gap-2">
            <button
              onClick={() => setSearchParams({})}
              className={`flex-1 p-2 rounded-lg font-bold transition ${activeTab === 'home' ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'}`}
            >
              الرئيسية
            </button>
            <button
              onClick={() => setSearchParams({ tab: 'following' })}
              className={`flex-1 p-2 rounded-lg font-bold transition ${activeTab === 'following' ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'}`}
            >
              المتابَعين
            </button>
          </div>

          <div className="glass-card p-3 mb-4">
            <input
              type="text"
              className="input-field"
              placeholder="ابحث في المنشورات..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              style={{ marginBottom: 0 }}
            />
          </div>

          <div className="glass-card p-4 mb-6">
            <form onSubmit={handleCreate}>
              <textarea
                className="input-field"
                placeholder="شارك أفكارك..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
              ></textarea>
              {imagePreviews.length > 0 && (
                <div className="mb-3">
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "8px" }}>
                    {imagePreviews.map((src, idx) => (
                      <div key={idx} className="glass-card p-1">
                        <img src={src} alt="preview" className="w-full rounded-lg" />
                      </div>
                    ))}
                  </div>
                  <div style={{ marginTop: 6, color: "var(--text-secondary)", fontSize: 12 }}>
                    {imagePreviews.length} صورة
                  </div>
                </div>
              )}
              <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={() => fileInputRef.current?.click()}
                >
                  إرفاق صورة
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handlePickImage}
                  style={{ display: "none" }}
                />
                <button
                  className="btn btn-primary w-auto px-6"
                  type="submit"
                  disabled={posting}
                >
                  {posting ? "جاري النشر..." : "نشر"}
                </button>
              </div>
            </form>
          </div>

          {loading && (
            <div className="space-y-4">
              <div className="glass-card p-6" style={{ height: 120, opacity: 0.6 }}></div>
              <div className="glass-card p-6" style={{ height: 120, opacity: 0.6 }}></div>
              <div className="glass-card p-6" style={{ height: 120, opacity: 0.6 }}></div>
            </div>
          )}

          {!loading && filteredPosts.map(post => (
            <div key={post.id} className="glass-card p-5 mb-4">
              <div className="flex items-center gap-3 mb-4 justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold">
                    {post.author_name?.charAt(0)}
                  </div>
                  <div>
                    <h4 className="font-bold">{post.author_name}</h4>
                    <span style={{ color: "var(--text-secondary)", fontSize: "12px" }}>
                      {post.author_type === "teacher" ? "مدرس" : "طالب"}
                    </span>
                  </div>
                </div>
                {(post.author_name === currentUserName || post.author_name === currentUserEmail) && (
                  <button
                    className="btn btn-outline"
                    onClick={async () => {
                      try {
                        await api.delete(`/posts/${post.id}/`);
                        setPosts(posts.filter(p => p.id !== post.id));
                      } catch {
                        alert('فشل حذف المنشور');
                      }
                    }}
                  >
                    حذف
                  </button>
                )}
              </div>

              <p className="mb-4">{post.content}</p>

              {post.images && post.images.length > 0 && (
                <div className="mb-4" style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: "8px" }}>
                  {post.images.slice(0, 4).map((img) => (
                    <img key={img.id} src={img.url} alt="" className="w-full rounded-lg" />
                  ))}
                </div>
              )}
              {(!post.images || post.images.length === 0) && post.image && (
                <img src={post.image} alt="" className="w-full rounded-lg mb-4" />
              )}

              <div className="flex gap-4 text-gray-500 border-t pt-4 border-white/10">
                <button onClick={() => handleLike(post.id)} className="flex items-center gap-2 hover:text-red-500 transition">
                  <Heart size={18} /> {post.likes_count} إعجاب
                </button>
                <button className="flex items-center gap-2 hover:text-blue-500 transition">
                  <MessageSquare size={18} /> تعليق
                </button>
                <button onClick={() => handleShare(post.id)} className="flex items-center gap-2 hover:text-green-500 transition">
                  <Share2 size={18} /> مشاركة
                </button>
              </div>
            </div>
          ))}

          {!loading && filteredPosts.length === 0 && (
            <div className="glass-card p-6 text-center" style={{ color: "var(--text-secondary)" }}>
              لا توجد منشورات مطابقة لبحثك
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Social;
