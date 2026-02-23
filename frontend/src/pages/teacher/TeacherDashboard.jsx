// src/pages/Teacher/TeacherDashboard.jsx
import React, { useState, useEffect } from "react";
import api from "../../api";

const TeacherDashboard = () => {
  const [serials, setSerials] = useState("");
  const [studentsData, setStudentsData] = useState([]);
  const [courses, setCourses] = useState([]);

  // جلب الكورسات عند الدخول
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const res = await api.get("/courses/");
        setCourses(res.data.results || res.data);
      } catch (err) {
        console.log(err);
      }
    };
    fetchCourses();
  }, []);

  // نقطة 7 و 21: البحث عن الطلاب بالسيريال نمبر
  const handleSearchStudents = async () => {
    const serialsList = serials.split("\n").filter((s) => s.trim() !== "");
    try {
      const res = await api.post("/students/lookup/", { serials: serialsList });
      setStudentsData(res.data);
    } catch (err) {
      alert("خطأ في البحث");
    }
  };

  // نقطة 20: تفعيل الطلاب
  const handleActivate = async (serial) => {
    const courseId = prompt("أدخل ID الكورس المطلوب تفعيله لهؤلاء الطلاب:"); // في التطبيق الحقيقي هيكون SelectList
    if (!courseId) return;

    try {
      await api.post("/bulk/activate-renew/", {
        serials: [serial],
        course_id: courseId,
      });
      alert("تم التفعيل بنجاح (35 يوم)");
    } catch (err) {
      alert("خطأ في التفعيل");
    }
  };

  return (
    <div className="min-h-screen p-6" dir="rtl">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="glass-card">
          <h2 className="text-2xl font-bold mb-4">لوحة تحكم المدرس</h2>
          <p className="text-gray-500">إدارة الكورسات والطلاب</p>
        </div>

        {/* قسم الكورسات */}
        <div className="glass-card">
          <h3 className="text-xl font-bold mb-3">كورساتك</h3>
          <div className="grid md:grid-cols-2 gap-4">
            {courses.map((course) => (
              <div
                key={course.id}
                className="bg-white/10 p-4 rounded-lg flex justify-between items-center"
              >
                <div>
                  <h4 className="font-bold">{course.title}</h4>
                  <p className="text-sm text-gray-400">{course.price} جنيه</p>
                </div>
                {course.cover_image && (
                  <img
                    src={course.cover_image}
                    alt=""
                    className="w-16 h-16 rounded object-cover"
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* قسم تفعيل الطلاب (نقطة 7) */}
        <div className="glass-card">
          <h3 className="text-xl font-bold mb-3">إضافة وتفعيل طلاب</h3>
          <textarea
            className="input-field h-32"
            placeholder="أدخل الأرقام التسلسلية (كل رقم في سطر)"
            value={serials}
            onChange={(e) => setSerials(e.target.value)}
          ></textarea>
          <button
            onClick={handleSearchStudents}
            className="btn-primary w-auto px-6 mt-2"
          >
            بحث عن الطلاب
          </button>

          {/* نتائج البحث */}
          {studentsData.length > 0 && (
            <div className="mt-6 border-t pt-4 border-white/10">
              <h4 className="font-bold mb-2">الطلاب الموجودين:</h4>
              {studentsData.map((s, idx) => (
                <div
                  key={idx}
                  className="flex justify-between items-center bg-white/5 p-3 rounded mb-2"
                >
                  <div>
                    <p>
                      <strong>الاسم:</strong> {s.name}
                    </p>
                    <p>
                      <strong>الهاتف:</strong> {s.phone}
                    </p>
                    <p>
                      <strong>ولي الأمر:</strong> {s.parent_phone}
                    </p>
                  </div>
                  <button
                    onClick={() => handleActivate(s.serial_number)}
                    className="bg-green-500 px-4 py-2 rounded-lg text-white text-sm hover:bg-green-600"
                  >
                    تفعيل اشتراك
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;
