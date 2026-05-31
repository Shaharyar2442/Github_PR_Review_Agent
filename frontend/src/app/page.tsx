"use client";
import { useEffect, useState } from "react";
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, X, AlertTriangle, Lightbulb, LogOut, Github } from 'lucide-react';

interface PendingReview {
  thread_id: string;
  owner: string;
  repo: string;
  pr_number: number;
  issues: string[];
  suggestions: string[];
}

export default function Dashboard() {
  const [reviews, setReviews] = useState<PendingReview[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchReviews = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiUrl}/pending`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (res.status === 401) {
        localStorage.removeItem('token');
        router.push('/login');
        return;
      }

      const data = await res.json();
      setReviews(data.pending_reviews || []);
    } catch (e) {
      console.error("Failed to fetch reviews", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, []);

  const handleApproval = async (thread_id: string, status: "approved" | "rejected") => {
    try {
      const token = localStorage.getItem('token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      
      // Optimistically remove the review from the UI for that snappy feel
      setReviews(reviews.filter(r => r.thread_id !== thread_id));

      await fetch(`${apiUrl}/approve`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ thread_id, status })
      });
      
    } catch (e) {
      console.error("Failed to approve", e);
      fetchReviews(); // revert on failure
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 text-slate-800 p-8 md:p-12 font-sans selection:bg-purple-200">
      <div className="max-w-5xl mx-auto">
        <header className="flex justify-between items-end mb-12">
          <div>
            <motion.h1 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-4xl md:text-5xl font-extrabold tracking-tight mb-2 bg-clip-text text-transparent bg-gradient-to-r from-purple-500 to-indigo-500"
            >
              Agentic Reviews
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-slate-500 text-lg font-medium"
            >
              Approve pending PR interventions
            </motion.p>
          </div>
          <button onClick={logout} className="flex items-center space-x-2 px-4 py-2 bg-white/50 hover:bg-white rounded-xl text-slate-600 transition shadow-sm border border-slate-200">
            <LogOut className="w-4 h-4" />
            <span className="text-sm font-medium">Logout</span>
          </button>
        </header>

        {loading ? (
          <div className="grid gap-6">
            {[1, 2].map(i => (
              <div key={i} className="h-64 rounded-3xl bg-white/40 animate-pulse border border-white/60"></div>
            ))}
          </div>
        ) : reviews.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-12 rounded-3xl bg-white/60 border border-white backdrop-blur-xl text-center text-slate-500 shadow-xl shadow-indigo-100/50"
          >
            <div className="w-20 h-20 bg-gradient-to-tr from-indigo-100 to-purple-100 rounded-full mx-auto flex items-center justify-center mb-6">
              <Check className="w-10 h-10 text-purple-400" />
            </div>
            <h2 className="text-2xl font-bold text-slate-700 mb-2">You're all caught up!</h2>
            <p>No pending reviews. Time to write some code.</p>
          </motion.div>
        ) : (
          <div className="grid gap-8">
            <AnimatePresence>
              {reviews.map((review) => (
                <motion.div 
                  key={review.thread_id} 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
                  layout
                  className="p-6 md:p-8 rounded-3xl bg-white/60 border border-white backdrop-blur-xl shadow-xl shadow-indigo-100/50 overflow-hidden relative"
                >
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-400 to-indigo-400"></div>
                  
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center">
                      <Github className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-slate-800">{review.repo} <span className="text-purple-500">#{review.pr_number}</span></h2>
                      <p className="text-slate-500 text-sm font-medium tracking-wide">Opened by {review.owner}</p>
                    </div>
                  </div>

                  {review.issues.length > 0 && (
                    <div className="mb-6 bg-red-50/80 border border-red-100 p-5 rounded-2xl">
                      <h3 className="text-red-500 font-bold mb-3 flex items-center space-x-2">
                        <AlertTriangle className="w-5 h-5" />
                        <span>Security & Bugs Found</span>
                      </h3>
                      <ul className="space-y-2">
                        {review.issues.map((issue, idx) => (
                          <li key={idx} className="flex items-start space-x-2 text-slate-700 text-sm">
                            <span className="text-red-400 mt-0.5">•</span>
                            <span>{issue}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {review.suggestions.length > 0 && (
                    <div className="mb-8 bg-emerald-50/80 border border-emerald-100 p-5 rounded-2xl">
                      <h3 className="text-emerald-600 font-bold mb-3 flex items-center space-x-2">
                        <Lightbulb className="w-5 h-5" />
                        <span>Agent Suggestions</span>
                      </h3>
                      <ul className="space-y-3">
                        {review.suggestions.map((sug, idx) => {
                          let text = sug;
                          if (Array.isArray(sug) && sug.length > 0 && sug[0].text) text = sug[0].text;
                          else if (typeof sug === 'object' && sug !== null && (sug as any).text) text = (sug as any).text;
                          else if (typeof text !== 'string') text = JSON.stringify(text);
                          
                          return (
                            <li key={idx} className="flex items-start space-x-2 text-slate-700 text-sm bg-white/50 p-3 rounded-xl border border-white">
                              <span>{text as string}</span>
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  )}

                  <div className="flex space-x-3 pt-4 border-t border-slate-100">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleApproval(review.thread_id, "approved")}
                      className="flex-1 flex items-center justify-center space-x-2 py-3 px-6 rounded-xl bg-gradient-to-r from-emerald-400 to-emerald-500 text-white font-semibold shadow-md shadow-emerald-200 hover:shadow-lg transition-all"
                    >
                      <Check className="w-5 h-5" />
                      <span>Approve PR</span>
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleApproval(review.thread_id, "rejected")}
                      className="flex items-center justify-center space-x-2 py-3 px-6 rounded-xl bg-white border border-rose-200 text-rose-500 font-semibold shadow-sm hover:bg-rose-50 transition-all"
                    >
                      <X className="w-5 h-5" />
                      <span>Reject</span>
                    </motion.button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </main>
  );
}
