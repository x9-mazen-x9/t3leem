// src/pages/Student/CourseDetail.jsx
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../api';

const CourseDetail = () => {
  const { id } = useParams();
  const [course, setCourse] = useState(null);
  const [unlockedLessons, setUnlockedLessons] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 1. جلب تفاصيل الكورس (والوحدات)
        const courseRes = await api.get(`/courses/${id}/`);
        setCourse(courseRes.data);

        // 2. جلب الدروس المفتوحة (للتأكد من الحالة)
        const unlockedRes = await api.get(`/lessons/unlocked/${id}/`);
        setUnlockedLessons(unlockedRes.data.unlocked_lesson_ids || []);
      } catch (err) {
        console.error(err);
      }
    };
    fetchData();
  }, [id]);

  if (!course) return <div className="text-center p-10">جاري التحميل...</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">{course.title}</h2>
      
      {/* عرض الوحدات */}
      {course.units && course.units.length > 0 ? (
        course.units.map((unit, index) => (
          <div key={unit.id} className="glass-card mb-4">
            <div className="p-4 border-b border-white/10">
              <h3 className="font-bold text-lg">الوحدة {index + 1}: {unit.title}</h3>
            </div>
            <div className="p-2">
              {/* هنا نفترض إن الدروس جاية مع الكورس أو هنطلبها لوحدها 
                  للتبسيط هنعرض شكل الدرس */}
              <div className="p-3 bg-white/5 rounded-lg mt-2 flex justify-between items-center">
                <span>درس تجريبي داخل الوحدة</span>
                <Link to={`/student/lesson/1`} className="text-indigo-400 hover:underline">
                  مشاهدة
                </Link>
              </div>
            </div>
          </div>
        ))
      ) : (
        <p>لا توجد وحدات في هذا الكورس حالياً.</p>
      )}
    </div>
  );
};

export default CourseDetail;