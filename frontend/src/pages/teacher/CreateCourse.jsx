import React, { useState } from "react";
import api from "../../api";

const CreateCourse = () => {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    price: "",
    access_type: "FREE", // or SEQUENTIAL
  });
  const [coverImage, setCoverImage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // نقطة 6: رفع البيانات والصورة
    const data = new FormData();
    data.append("cover_image", coverImage);
    Object.keys(formData).forEach((key) => data.append(key, formData[key]));

    try {
      await api.post("/courses/", data, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("تم إنشاء الكورس بنجاح!");
    } catch (err) {
      console.error(err);
      alert("حدث خطأ");
    }
  };

  return (
    <div className="min-h-screen p-6" dir="rtl">
      <div className="max-w-2xl mx-auto glass-card p-8">
        <h2 className="text-2xl font-bold mb-6">إنشاء كورس جديد</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="عنوان الكورس"
            className="input-field"
            onChange={(e) =>
              setFormData({ ...formData, title: e.target.value })
            }
            required
          />

          <textarea
            placeholder="وصف الكورس"
            className="input-field h-32"
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
          ></textarea>

          <input
            type="number"
            placeholder="السعر (جنيه)"
            className="input-field"
            onChange={(e) =>
              setFormData({ ...formData, price: e.target.value })
            }
          />

          <div className="flex items-center gap-4">
            <label className="font-bold">نوع الوصول:</label>
            <select
              className="input-field w-auto"
              onChange={(e) =>
                setFormData({ ...formData, access_type: e.target.value })
              }
            >
              <option value="FREE">مفتوح (Free)</option>
              <option value="SEQUENTIAL">تسلسلي (واجبات)</option>
            </select>
          </div>

          {/* صورة الغلاف */}
          <div>
            <label className="block mb-2 font-bold">صورة الغلاف</label>
            <input
              type="file"
              accept="image/*"
              className="input-field"
              onChange={(e) => setCoverImage(e.target.files[0])}
            />
          </div>

          <button type="submit" className="btn-primary">
            نشر الكورس
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreateCourse;
