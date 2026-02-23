// src/pages/Social.jsx
import React, { useEffect, useState } from 'react';
import api from '../api'; // تعديل المسار عشان طلعنا من فولدر Student

const Social = () => {
  const [posts, setPosts] = useState([]);
  const [newPostContent, setNewPostContent] = useState('');

  const fetchPosts = async () => {
    try {
      const res = await api.get('/posts/');
      setPosts(res.data.results || res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, []);

  const handleLike = async (postId) => {
    try {
      await api.post(`/posts/${postId}/like/`);
      fetchPosts(); 
    } catch (err) {
      alert('حدث خطأ أثناء الإعجاب');
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    if(!newPostContent.trim()) return;
    try {
        // الباك اند هيحدد لو المستخدم ده طالب ولا مدرس لوحدو
        // ولو مدرس وهيطلع Error لو الاشتراك منتهي (Point 13)
        await api.post('/posts/', { 
            title: "منشور جديد", 
            content: newPostContent 
        });
        setNewPostContent('');
        fetchPosts();
    } catch (err) {
        // لو المدرس مجمد (منتهي الاشتراك)، الباك اند هيبعت رسالة واضحة
        const errorMsg = err.response?.data?.detail || "حدث خطأ أثناء النشر";
        alert(errorMsg);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* صندوق النشر */}
      <div className="glass-card p-6 mb-6">
        <form onSubmit={handleCreatePost}>
          <textarea 
            className="input-field h-24 resize-none"
            placeholder="شارك أفكارك مع المجتمع..."
            value={newPostContent}
            onChange={(e) => setNewPostContent(e.target.value)}
          ></textarea>
          <button type="submit" className="btn btn-primary mt-2 w-auto px-6">
            نشر الآن
          </button>
        </form>
      </div>

      {/* البوستات */}
      {posts.length === 0 && <p className="text-center text-gray-400">لا توجد منشورات حتى الآن.</p>}
      
      {posts.map(post => (
        <div key={post.id} className="glass-card p-6 mb-4">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold">
              {post.author_name?.charAt(0)}
            </div>
            <div>
              <h4 className="font-bold flex items-center gap-1">
                {post.author_name}
                {/* علامة التوثيق (Point 4) */}
                {post.author_verified && <i className="fas fa-check-circle text-blue-400 text-sm"></i>}
              </h4>
              <p className="text-xs text-gray-400">{new Date(post.created_at).toLocaleDateString('ar-EG')}</p>
            </div>
          </div>
          
          <p className="mb-4 whitespace-pre-wrap">{post.content}</p>
          
          {post.image && <img src={post.image} alt="" className="rounded-lg w-full mb-4 max-h-96 object-cover" />}

          <div className="flex gap-6 text-gray-400 border-t border-white/10 pt-4">
            <button onClick={() => handleLike(post.id)} className="flex items-center gap-2 hover:text-red-400 transition-colors">
              <i className="far fa-heart"></i> {post.likes_count} إعجاب
            </button>
            <button className="flex items-center gap-2 hover:text-blue-400 transition-colors">
              <i className="far fa-comment"></i> تعليق
            </button>
            <button className="flex items-center gap-2 hover:text-green-400 transition-colors">
              <i className="far fa-share-square"></i> مشاركة
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Social;