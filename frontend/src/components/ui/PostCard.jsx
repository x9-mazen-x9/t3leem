import React from "react";
import Card from "./Card";
import { Heart, MessageSquare, Share2 } from "lucide-react";

const PostCard = ({ post, onLike, onShare }) => {
  const initials = post?.author_name ? post.author_name.charAt(0) : "?";
  return (
    <Card className="p-5">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-500 text-white">
          {initials}
        </div>
        <div>
          <div className="font-bold">{post.author_name}</div>
          <div className="text-xs text-slate-500 dark:text-slate-400">
            {post.author_type === "teacher" ? "مدرس" : "طالب"}
          </div>
        </div>
      </div>

      <div className="mb-4 whitespace-pre-wrap text-[15px] leading-7">
        {post.content}
      </div>

      {post.image && (
        <img
          src={post.image}
          alt=""
          className="mb-4 w-full rounded-xl object-cover"
        />
      )}

      <div className="mt-2 flex items-center gap-6 border-t border-white/10 pt-4 text-slate-600 dark:text-slate-300">
        <button
          onClick={() => onLike?.(post.id)}
          className="inline-flex items-center gap-2 rounded-xl px-2 py-1 hover:text-rose-500"
        >
          <Heart size={18} /> {post.likes_count} إعجاب
        </button>
        <button className="inline-flex items-center gap-2 rounded-xl px-2 py-1 hover:text-indigo-500">
          <MessageSquare size={18} /> تعليق
        </button>
        <button
          onClick={() => onShare?.(post.id)}
          className="inline-flex items-center gap-2 rounded-xl px-2 py-1 hover:text-emerald-600"
        >
          <Share2 size={18} /> مشاركة
        </button>
      </div>
    </Card>
  );
};

export default PostCard;
