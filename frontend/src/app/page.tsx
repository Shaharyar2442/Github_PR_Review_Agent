"use client";
import { useEffect, useState } from "react";

// The data structure of a pending review
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

  // Fetch the pending reviews from our FastAPI backend
  const fetchReviews = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiUrl}/pending`);
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

  // Function to approve or reject a review
  const handleApproval = async (thread_id: string, status: "approved" | "rejected") => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      await fetch(`${apiUrl}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thread_id, status })
      });
      // Re-fetch after handling
      fetchReviews();
    } catch (e) {
      console.error("Failed to approve", e);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white p-12 font-sans selection:bg-indigo-500">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-5xl font-extrabold tracking-tight mb-2 bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">
          Agent Dashboard
        </h1>
        <p className="text-slate-400 mb-12 text-lg">Manage pending AI code reviews.</p>

        {loading ? (
          <div className="animate-pulse flex space-x-4">
            <div className="flex-1 space-y-4 py-1">
              <div className="h-4 bg-slate-700 rounded w-3/4"></div>
              <div className="h-4 bg-slate-700 rounded"></div>
            </div>
          </div>
        ) : reviews.length === 0 ? (
          <div className="p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md text-center text-slate-300">
            No pending reviews right now! Take a break ☕
          </div>
        ) : (
          <div className="grid gap-6">

            {reviews.map((review) => (
              <div key={review.thread_id} className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md shadow-xl transition hover:bg-white/10">
                <h2 className="text-2xl font-bold mb-1 text-indigo-300">{review.repo} - PR #{review.pr_number}</h2>
                <p className="text-slate-400 mb-4 text-sm font-medium tracking-wide uppercase">Owner: {review.owner}</p>

                {review.issues.length > 0 && (
                  <div className="mb-4 bg-red-900/20 border border-red-500/20 p-4 rounded-xl">
                    <h3 className="text-red-400 font-semibold mb-2">🚨 Issues Found</h3>
                    <ul className="list-disc list-inside space-y-1 text-red-200/80 text-sm">
                      {review.issues.map((issue, idx) => (
                        <li key={idx}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {review.suggestions.length > 0 && (
                  <div className="mb-6 bg-emerald-900/20 border border-emerald-500/20 p-4 rounded-xl">
                    <h3 className="text-emerald-400 font-semibold mb-2">💡 Suggestions</h3>
                    <ul className="list-disc list-inside space-y-1 text-emerald-200/80 text-sm">
                      {review.suggestions.map((sug, idx) => {
                        let text = sug;
                        // Handle LangChain message content arrays
                        if (Array.isArray(sug) && sug.length > 0 && sug[0].text) {
                            text = sug[0].text;
                        } else if (typeof sug === 'object' && sug !== null && (sug as any).text) {
                            text = (sug as any).text;
                        } else if (typeof text !== 'string') {
                            text = JSON.stringify(text);
                        }
                        
                        return <li key={idx}>{text as string}</li>;
                      })}
                    </ul>
                  </div>
                )}
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleApproval(review.thread_id, "approved")}
                    className="px-4 py-2 rounded-lg bg-green-600 hover:bg-green-700"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => handleApproval(review.thread_id, "rejected")}
                    className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700"
                  >
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
