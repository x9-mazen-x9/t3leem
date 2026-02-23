import React from 'react';
import { BookOpen, Clock, Award } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export default function Dashboard() {
  const { user } = useAuth();
  const { t, theme } = useLanguage();

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="mb-10 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {t.dash_welcome}, {user?.first_name || user?.email?.split('@')[0]}!
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Here is your learning progress.</p>
        </div>
        <img 
          src={`/logo-${theme === 'dark' ? 'white' : 'black'}.png`} 
          alt="Logo" 
          className="h-10 w-auto"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {[
          { label: t.dash_stats_courses, val: "12", icon: BookOpen, color: "text-blue-500", bg: "bg-blue-100 dark:bg-blue-900/20" },
          { label: t.dash_stats_hours, val: "48h", icon: Clock, color: "text-purple-500", bg: "bg-purple-100 dark:bg-purple-900/20" },
          { label: "Certificates", val: "5", icon: Award, color: "text-green-500", bg: "bg-green-100 dark:bg-green-900/20" },
        ].map((stat, i) => (
          <div key={i} className="glass p-6 rounded-2xl border border-white/20 dark:border-white/5 flex items-center gap-4">
            <div className={`w-14 h-14 rounded-xl ${stat.bg} flex items-center justify-center`}>
              <stat.icon size={24} className={stat.color} />
            </div>
            <div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{stat.val}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="glass rounded-2xl p-6 border border-white/20 dark:border-white/5">
        <h3 className="text-xl font-bold mb-6 text-gray-900 dark:text-white">Recent Courses</h3>
        <div className="space-y-4">
          {[1, 2, 3].map((item) => (
            <div key={item} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-primary-600 dark:text-primary-400 font-bold">
                  {item}
                </div>
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">Advanced React Patterns</p>
                  <p className="text-sm text-gray-500">Module {item} • 2h 15m remaining</p>
                </div>
              </div>
              <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-primary-600 h-2 rounded-full" style={{ width: `${item * 30}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}