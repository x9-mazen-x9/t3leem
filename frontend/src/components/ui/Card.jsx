import React from "react";

const Card = ({ className = "", children }) => {
  return (
    <div
      className={
        "rounded-2xl border border-white/10 bg-white/70 dark:bg-slate-900/60 backdrop-blur p-5 shadow-md dark:shadow-black/20 " +
        className
      }
    >
      {children}
    </div>
  );
};

export default Card;
