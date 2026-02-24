import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api';

const Social = () => {
  const [posts, setPosts] = useState([]);
  const [searchParams, setSearchParams] = useSearchParams();
  
  // تحديد التبويب النشط
  const activeTab = searchParams.get("tab") || "home";

  useEffect(() => {
    let url = '/posts/';
    if (activeTab === "following") {
        // نفترض إن عندك فلتر في الباك إند posts/?following=true
        // أو هنجيب بوستات المدرسين اللي بعملهم follow من الـ client side
        // للتبسيط هنستخدم الـ API العادي
    }
    
    api.get(url).then(res => setPosts(res.data.results || res.data));

  }, [activeTab]);

  return (
    <div className="social-feed-page" style={{ padding: '30px 0', background: 'var(--bg-color)', minHeight: '100vh' }}>
        <div className="container mx-auto" style={{ maxWidth: '600px' }}>
            
            {/* التبويبات (نقطة 3) */}
            <div className="glass-card flex mb-6 p-2 gap-2">
                <button 
                    onClick={() => setSearchParams({})} 
                    className={`flex-1 p-2 rounded-lg font-bold transition ${activeTab === 'home' ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'}`}
                >
                    <i className="fas fa-home ml-2"></i> الرئيسية
                </button>
                <button 
                    onClick={() => setSearchParams({ tab: 'following' })} 
                    className={`flex-1 p-2 rounded-lg font-bold transition ${activeTab === 'following' ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'}`}
                >
                    <i className="fas fa-user-friends ml-2"></i> المتابَعين
                </button>
            </div>

            {/* صندوق النشر */}
            <div className="glass-card p-4 mb-6">
                <textarea className="input-field" placeholder="شارك أفكارك..."></textarea>
                <button className="btn btn-primary w-auto px-6 mt-2">نشر</button>
            </div>

            {/* البوستات */}
            {posts.map(post => (
                <div key={post.id} className="glass-card p-4 mb-4">
                    <h4 className="font-bold mb-2">{post.author_name}</h4>
                    <p>{post.content}</p>
                    {/* باقي تفاصيل البوست */}
                </div>
            ))}
        </div>
    </div>
  );
};

export default Social;