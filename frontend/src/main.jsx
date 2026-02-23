// src/main.jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// 1. استيراد الـ Provider اللي عملناه في الخطوة السابقة
import { AuthProvider } from './context/AuthContext.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    
    {/* 2. تغليف الـ App بالـ Provider 
       ده معناه إن أي صفحة جوه الـ App تقدر توصل لبيانات المستخدم */}
    <AuthProvider>
      <App />
    </AuthProvider>

  </React.StrictMode>,
);