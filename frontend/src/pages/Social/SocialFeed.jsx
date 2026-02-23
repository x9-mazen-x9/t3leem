import React, { useState, useEffect } from "react";
import api from "../../api";

const SocialFeed = () => {
  const [posts, setPosts] = useState([]);
  const [content, setContent] = useState("");

  // جلب البوستات
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const res = await api.get("/posts/");
        setPosts(res.data.results || res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchPosts();
  }, []);

  // إنشاء بوست جديد
  const handlePost = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post("/posts/", { title: "منشور", content });
      setPosts([res.data, ...posts]);
      setContent("");
    } catch (err) {
      alert("خطأ في النشر");
    }
  };

  // لايك (Point 5)
  const handleLike = async (postId) => {
    try {
      await api.post(`/posts/${postId}/like/`);
      // تحديث الـ UI
      setPosts(
        posts.map((p) =>
          p.id === postId ? { ...p, likes_count: p.likes_count + 1 } : p,
        ),
      );
    } catch (err) {}
  };

  return (
    <div className="min-h-screen p-6" dir="rtl">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* صندوق إنشاء بوست */}
        <div className="glass-card p-6">
          <form onSubmit={handlePost}>
            <textarea
              className="input-field h-24"
              placeholder="شارك أفكارك..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
            ></textarea>
            <button type="submit" className="btn-primary mt-2 w-auto px-6">
              نشر
            </button>
          </form>
        </div>

        {/* عرض البوستات */}
        {posts.map((post) => (
          <div key={post.id} className="glass-card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold">
                {post.author_name?.charAt(0)}
              </div>
              <div>
                <h4 className="font-bold">{post.author_name}</h4>
                <span className="text-xs text-gray-400">
                  {post.author_type === "teacher" && (
                    <i className="fas fa-check-circle text-blue-500 ml-1"></i>
                  )}
                  {post.author_type === "teacher" ? "مدرس" : "طالب"}
                </span>
              </div>
            </div>

            <p className="mb-4">{post.content}</p>

            {/* صورة البوست */}
            {post.image && (
              <img src={post.image} alt="" className="w-full rounded-lg mb-4" />
            )}

            <div className="flex gap-4 text-gray-500 border-t pt-4 border-white/10">
              <button
                onClick={() => handleLike(post.id)}
                className="flex items-center gap-2 hover:text-red-500 transition"
              >
                <i className="far fa-heart"></i> {post.likes_count} إعجاب
              </button>
              <button className="flex items-center gap-2 hover:text-blue-500 transition">
                <i className="far fa-comment"></i> تعليق
              </button>
              <button className="flex items-center gap-2 hover:text-green-500 transition">
                <i className="far fa-share-square"></i> مشاركة
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SocialFeed;
