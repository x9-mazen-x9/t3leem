// src/pages/Student/Courses.jsx
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api';

const Courses = () => {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const res = await api.get('/courses/');
        setCourses(res.data.results || res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchCourses();
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">كورساتي الدراسية</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map(course => (
          <div key={course.id} className="glass-card overflow-hidden">
            <img 
              src={course.cover_image || 'https://via.placeholder.com/400x200'} 
              alt={course.title} 
              className="w-full h-40 object-cover"
            />
            <div className="p-5">
              <h3 className="font-bold text-lg mb-2">{course.title}</h3>
              <p className="text-sm text-gray-400 mb-4">{course.description?.substring(0, 50)}...</p>
              
              <Link 
                to={`/student/courses/${course.id}`} 
                className="btn btn-primary w-full text-center block"
              >
                متابعة الدراسة
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Courses;