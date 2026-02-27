import React from "react";
import { Outlet } from "react-router-dom";
import NavBar from "../components/NavBar";

const MainLayout = () => {
  return (
    <div className="relative min-h-screen" dir="rtl">
      <div className="bg-blob blob-1"></div>
      <div className="bg-blob blob-2"></div>
      <NavBar />
      <main className="relative mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
