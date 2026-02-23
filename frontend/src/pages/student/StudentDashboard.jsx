import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../../api";

const StudentDashboard = () => {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        // جلب الكورسات اللي الطالب مشترك فيها
        const res = await api.get("/courses/");
        setCourses(res.data.results || res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchCourses();
  }, []);

  return (
    <div className="min-h-screen p-6" dir="rtl">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-black mb-8">كورساتي</h1>

        <div className="grid md:grid-cols-3 gap-6">
          {courses.map((course) => (
            <Link
              to={`/student/course/${course.id}`}
              key={course.id}
              className="glass-card block hover:scale-105 transition-transform"
            >
              {course.cover_image && (
                <img
                  src={course.cover_image}
                  alt={course.title}
                  className="w-full h-40 object-cover rounded-lg mb-4"
                />
              )}
              <h3 className="text-xl font-bold">{course.title}</h3>
              <p className="text-gray-400 mt-2">{course.teacher_name}</p>
              <div className="mt-4 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                {/* Placeholder for progress bar */}
                <div
                  className="bg-indigo-500 h-2 rounded-full"
                  style={{ width: "30%" }}
                ></div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
