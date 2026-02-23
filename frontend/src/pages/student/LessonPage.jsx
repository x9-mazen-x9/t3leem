// src/pages/Student/LessonPage.jsx
import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../api';

const LessonPage = () => {
  const { lessonId } = useParams();
  const [lesson, setLesson] = useState(null);
  const videoRef = useRef(null);

  useEffect(() => {
    const fetchLesson = async () => {
      try {
        const res = await api.get(`/lessons/${lessonId}/`);
        setLesson(res.data);
      } catch (err) {
        console.error("Error loading lesson", err);
      }
    };
    fetchLesson();
  }, [lessonId]);

  // دالة حفظ التقدم (نقطة 11 - استئناف التقدم)
  const saveProgress = async (currentTime, duration) => {
    if (currentTime > 0 && duration > 0) {
      try {
        await api.post('/progress/save/', {
          lesson_id: lessonId,
          last_second: Math.floor(currentTime),
          total_seconds: Math.floor(duration)
        });
      } catch (err) {
        console.error("Error saving progress", err);
      }
    }
  };

  // تحديث التقدم كل 10 ثواني أو عند الإيقاف
  const handleTimeUpdate = (e) => {
    const video = e.target;
    // حل مبدئي: حفظ كل 30 ثانية
    if (Math.floor(video.currentTime) % 30 === 0) {
       saveProgress(video.currentTime, video.duration);
    }
  };

  if (!lesson) return <div className="text-center p-10">جاري تحميل الدرس...</div>;

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      {/* الفيديو */}
      <div className="lg:col-span-2">
        <div className="glass-card p-2" style={{ background: '#000' }}>
          {lesson.video_url ? (
            <iframe 
              src={lesson.video_url}
              style={{ width: '100%', height: '400px', border: 'none' }}
              allowFullScreen
              title="Lesson Video"
            ></iframe>
          ) : (
            <div className="text-center p-20 text-white">الفيديو غير متاح</div>
          )}
        </div>
        
        <div className="glass-card mt-4 p-6">
          <h2 className="text-xl font-bold mb-2">{lesson.title}</h2>
          <p className="text-gray-400">{lesson.description}</p>
        </div>
      </div>

      {/* المرفقات والواجب */}
      <div className="lg:col-span-1">
        <div className="glass-card p-4 mb-4">
          <h3 className="font-bold mb-3"><i className="fas fa-file-alt ml-2"></i>ملحقات الدرس</h3>
          {lesson.lesson_material ? (
            <a href={lesson.lesson_material} download className="btn btn-primary w-full text-center block">
              تحميل الملف (PDF)
            </a>
          ) : (
            <p className="text-gray-400 text-sm">لا توجد مرفقات</p>
          )}
        </div>

        {/* الواجب */}
        {lesson.has_homework && (
          <div className="glass-card p-4 bg-green-500/10 border border-green-500/20">
            <h3 className="font-bold mb-3 text-green-400">واجب هذا الدرس</h3>
            <button 
              onClick={async () => {
                  try {
                      await api.post('/progress/submit-homework/', { lesson_id: lessonId });
                      alert('تم تسليم الواجب بنجاح!');
                  } catch(err) {
                      alert('خطأ في التسليم');
                  }
              }}
              className="btn btn-primary w-full bg-green-600"
            >
              تسليم الواجب
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default LessonPage;