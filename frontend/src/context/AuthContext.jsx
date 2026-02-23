import React, { createContext, useState, useEffect } from "react";
import api from "../api";
export const AuthContext = createContext();
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          const res = await api.get("/auth/me/");
          setUser(res.data);
          localStorage.setItem("user_type", res.data.user_type);
        } catch (err) {
          localStorage.removeItem("access_token");
        }
      }
      setLoading(false);
    };
    fetchUser();
  }, []);
  return (
    <AuthContext.Provider value={{ user, setUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
