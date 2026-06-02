"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import {
  Check, X, AlertTriangle, Lightbulb, LogOut,
  GitBranch, GitPullRequest, Plus, RefreshCw,
  ChevronDown, ChevronUp, ExternalLink,
} from "lucide-react";
import Logo from "./components/Logo";
import LoadingState from "./components/LoadingState";
import ThemeToggle from "./components/ThemeToggle";

interface PendingReview {
  thread_id: string;
  owner: string;
  repo: string;
  pr_number: number;
  issues: string[];
  suggestions: string[];
}

const POLL_INTERVAL_MS = 3000;

// Normalise LLM output — Gemini sometimes returns lists of content blocks
function normaliseText(raw: unknown): string {
  if (typeof raw === "string") return raw;
  if (Array.isArray(raw)) {
    return raw
      .map((b) => (typeof b === "object" && b !== null && "text" in b ? (b as { text: string }).text : ""))
      .filter(Boolean)
      .join("\n");
  }
  if (typeof raw === "object" && raw !== null && "text" in raw) return (raw as { text: string }).text;
  return JSON.stringify(raw);
}

export default function Dashboard() {
  const [reviews, setReviews] = useState<PendingReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedCards, setExpandedCards] = useState<Record<string, "issues" | "suggestions">>({});
  const [approvingId, setApprovingId] = useState<string | null>(null);
  const router = useRouter();
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Core fetch ──────────────────────────────────────────────
  const fetchReviews = useCallback(async (silent = false) => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
    if (!silent) setRefreshing(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiUrl}/pending`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.status === 401) {
        localStorage.removeItem("token");
        router.push("/login");
        return;
      }
      const data = await res.json();
      setReviews(data.pending_reviews || []);
    } catch {
      // Silently fail on background polls — don't disrupt UX
    } finally {
      setLoading(false);
      if (!silent) setRefreshing(false);
    }
  }, [router]);

  // ── Initial load + polling ─────────────────────────────────
  useEffect(() => {
    fetchReviews(false);

    // Poll every 3 s while dashboard is open
    pollingRef.current = setInterval(() => fetchReviews(true), POLL_INTERVAL_MS);
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [fetchReviews]);

  // ── Approval / rejection ───────────────────────────────────
  const handleApproval = async (thread_id: string, status: "approved" | "rejected") => {
    const token = localStorage.getItem("token");
    if (!token) return;
    setApprovingId(thread_id);
    // Optimistic removal
    setReviews((prev) => prev.filter((r) => r.thread_id !== thread_id));
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      await fetch(`${apiUrl}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ thread_id, status }),
      });
    } catch {
      // On failure, re-fetch to get accurate state
      fetchReviews(false);
    } finally {
      setApprovingId(null);
    }
  };

  const logout = () => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    localStorage.removeItem("token");
    router.push("/login");
  };

  const toggleTab = (threadId: string, tab: "issues" | "suggestions") => {
    setExpandedCards((prev) => ({ ...prev, [threadId]: tab }));
  };

  const githubAppUrl = process.env.NEXT_PUBLIC_GITHUB_APP_URL;

  // ─── Render ───────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-surface-2 flex flex-col">
      {/* ── Navbar ── */}
      <header className="sticky top-0 z-40 h-16 border-b border-border bg-surface/80 backdrop-blur-md flex items-center px-4 md:px-8 gap-4">
        {/* Brand */}
        <div className="flex items-center gap-2.5 flex-shrink-0">
          <Logo size={30} />
          <span className="font-bold text-base text-text-primary hidden sm:block">ReviewBot</span>
        </div>

        <div className="flex-1" />

        {/* Actions */}
        <div className="flex items-center gap-2">
          {/* Connect repository */}
          {githubAppUrl && (
            <motion.a
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              href={githubAppUrl}
              target="_blank"
              rel="noopener noreferrer"
              id="connect-repo-btn"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold text-white bg-red-primary hover:bg-red-deep shadow-sm shadow-red-primary/20 transition-all"
            >
              <Plus className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Connect Repo</span>
              <ExternalLink className="w-3 h-3 opacity-70" />
            </motion.a>
          )}

          {/* Manual refresh */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => fetchReviews(false)}
            disabled={refreshing}
            id="refresh-btn"
            aria-label="Refresh reviews"
            className="w-9 h-9 rounded-xl flex items-center justify-center border border-border bg-surface-2 text-text-secondary hover:text-text-primary transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
          </motion.button>

          <ThemeToggle />

          {/* Logout */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={logout}
            id="logout-btn"
            aria-label="Logout"
            className="w-9 h-9 rounded-xl flex items-center justify-center border border-border bg-surface-2 text-text-secondary hover:text-red-primary hover:border-red-primary/30 transition-all"
          >
            <LogOut className="w-4 h-4" />
          </motion.button>
        </div>
      </header>

      {/* ── Main content ── */}
      <main className="flex-1 max-w-3xl w-full mx-auto px-4 md:px-6 py-8">
        {/* Page heading */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-2xl font-extrabold text-text-primary mb-1 flex items-center gap-2">
            <GitPullRequest className="w-6 h-6 text-red-primary" />
            Pending Reviews
          </h1>
          <p className="text-text-secondary text-sm">
            AI-analyzed pull requests awaiting your approval.{" "}
            {!loading && reviews.length > 0 && (
              <span className="inline-flex items-center gap-1 ml-1 px-2 py-0.5 rounded-full bg-red-primary/10 text-red-primary text-xs font-semibold">
                {reviews.length} pending
              </span>
            )}
          </p>
        </motion.div>

        {/* ── States ── */}
        {loading ? (
          <LoadingState />
        ) : reviews.length === 0 ? (
          <EmptyState githubAppUrl={githubAppUrl} />
        ) : (
          <div className="grid gap-5">
            <AnimatePresence initial={false}>
              {reviews.map((review, idx) => {
                const activeTab = expandedCards[review.thread_id] ?? "issues";
                return (
                  <motion.article
                    key={review.thread_id}
                    layout
                    initial={{ opacity: 0, y: 24 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.97, transition: { duration: 0.18 } }}
                    transition={{ delay: idx * 0.06, duration: 0.35 }}
                    className="rounded-2xl bg-surface border border-border overflow-hidden shadow-sm hover:shadow-md hover:border-border transition-all"
                  >
                    {/* Card top accent */}
                    <div className="h-[3px] bg-gradient-to-r from-red-primary to-red-glow" />

                    {/* Header */}
                    <div className="flex items-start justify-between px-5 pt-5 pb-4 gap-3">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-9 h-9 rounded-xl bg-red-primary/10 border border-red-primary/20 flex items-center justify-center flex-shrink-0">
                          <GitBranch className="w-4 h-4 text-red-primary" />
                        </div>
                        <div className="min-w-0">
                          <h2 className="text-base font-bold text-text-primary flex items-center gap-2 flex-wrap">
                            <span className="truncate">{review.repo}</span>
                            <span className="text-red-primary font-mono text-sm flex-shrink-0">
                              #{review.pr_number}
                            </span>
                          </h2>
                          <p className="text-xs text-text-muted mt-0.5">
                            by{" "}
                            <span className="font-medium text-text-secondary">{review.owner}</span>
                          </p>
                        </div>
                      </div>

                      {/* Issue count badge */}
                      {review.issues.length > 0 && (
                        <span className="flex-shrink-0 flex items-center gap-1 px-2 py-1 rounded-lg bg-red-muted border border-red-primary/15 text-red-primary text-xs font-bold">
                          <AlertTriangle className="w-3 h-3" />
                          {review.issues.length}
                        </span>
                      )}
                    </div>

                    {/* Tabs */}
                    <div className="flex border-t border-border">
                      {(["issues", "suggestions"] as const).map((tab) => {
                        const count = tab === "issues" ? review.issues.length : review.suggestions.length;
                        const isActive = activeTab === tab;
                        return (
                          <button
                            key={tab}
                            onClick={() => toggleTab(review.thread_id, tab)}
                            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-semibold uppercase tracking-wider transition-all ${
                              isActive
                                ? "text-text-primary border-b-2 border-red-primary bg-surface-2"
                                : "text-text-muted hover:text-text-secondary"
                            }`}
                          >
                            {tab === "issues" ? (
                              <AlertTriangle className="w-3 h-3" />
                            ) : (
                              <Lightbulb className="w-3 h-3" />
                            )}
                            {tab} ({count})
                            {isActive ? (
                              <ChevronUp className="w-3 h-3 ml-auto opacity-60" />
                            ) : (
                              <ChevronDown className="w-3 h-3 ml-auto opacity-40" />
                            )}
                          </button>
                        );
                      })}
                    </div>

                    {/* Tab content */}
                    <div className="px-5 py-4">
                      <AnimatePresence mode="wait" initial={false}>
                        {activeTab === "issues" ? (
                          <motion.div
                            key="issues"
                            initial={{ opacity: 0, y: 6 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -6 }}
                            transition={{ duration: 0.18 }}
                          >
                            {review.issues.length === 0 ? (
                              <p className="text-text-muted text-sm py-2">No issues found. 🎉</p>
                            ) : (
                              <ul className="space-y-2">
                                {review.issues.map((issue, i) => (
                                  <li
                                    key={i}
                                    className="flex items-start gap-2.5 text-sm text-text-primary"
                                  >
                                    <span className="mt-0.5 w-4 h-4 rounded-full bg-red-muted border border-red-primary/20 flex items-center justify-center flex-shrink-0">
                                      <AlertTriangle className="w-2.5 h-2.5 text-red-primary" />
                                    </span>
                                    <span className="leading-relaxed">{normaliseText(issue)}</span>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </motion.div>
                        ) : (
                          <motion.div
                            key="suggestions"
                            initial={{ opacity: 0, y: 6 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -6 }}
                            transition={{ duration: 0.18 }}
                          >
                            {review.suggestions.length === 0 ? (
                              <p className="text-text-muted text-sm py-2">No suggestions yet.</p>
                            ) : (
                              <ul className="space-y-4">
                                {review.suggestions.map((sug, i) => (
                                  <li key={i} className="rounded-xl border border-border bg-surface-2 overflow-hidden">
                                    <div className="px-1 py-1">
                                      {/* react-markdown with @tailwindcss/typography prose */}
                                      <div className="prose prose-sm prose-review max-w-none dark:prose-invert px-3 py-2">
                                        <ReactMarkdown>
                                          {normaliseText(sug)}
                                        </ReactMarkdown>
                                      </div>
                                    </div>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>

                    {/* Action buttons */}
                    <div className="flex gap-3 px-5 pb-5 pt-1">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.97 }}
                        id={`approve-btn-${review.pr_number}`}
                        onClick={() => handleApproval(review.thread_id, "approved")}
                        disabled={approvingId === review.thread_id}
                        className="flex-1 flex items-center justify-center gap-2 py-2.5 px-5 rounded-xl text-sm font-semibold text-white bg-green-accent hover:bg-emerald-600 shadow-sm shadow-green-accent/20 transition-all disabled:opacity-50"
                      >
                        <Check className="w-4 h-4" />
                        Approve & Post
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.97 }}
                        id={`reject-btn-${review.pr_number}`}
                        onClick={() => handleApproval(review.thread_id, "rejected")}
                        disabled={approvingId === review.thread_id}
                        className="flex items-center justify-center gap-2 py-2.5 px-5 rounded-xl text-sm font-semibold border border-border text-text-secondary hover:text-red-primary hover:border-red-primary/40 hover:bg-red-muted transition-all disabled:opacity-50"
                      >
                        <X className="w-4 h-4" />
                        Reject
                      </motion.button>
                    </div>
                  </motion.article>
                );
              })}
            </AnimatePresence>
          </div>
        )}
      </main>
    </div>
  );
}

// ── Empty state ──────────────────────────────────────────────
function EmptyState({ githubAppUrl }: { githubAppUrl?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex flex-col items-center justify-center py-24 text-center"
    >
      {/* Floating icon */}
      <div className="relative mb-6">
        <div className="w-20 h-20 rounded-2xl bg-red-primary/10 border border-red-primary/20 flex items-center justify-center" style={{ animation: "float 3s ease-in-out infinite" }}>
          <Check className="w-10 h-10 text-red-primary" />
        </div>
        <div className="absolute -inset-2 rounded-2xl bg-red-primary/5 blur-xl -z-10" />
      </div>

      <h2 className="text-xl font-bold text-text-primary mb-2">All clear!</h2>
      <p className="text-text-secondary text-sm max-w-xs leading-relaxed mb-8">
        No pending reviews right now. Open a pull request on a connected repo to trigger AI analysis.
      </p>

      {githubAppUrl && (
        <motion.a
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          href={githubAppUrl}
          target="_blank"
          rel="noopener noreferrer"
          id="connect-repo-empty-btn"
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-red-primary hover:bg-red-deep shadow-lg shadow-red-primary/25 transition-all"
        >
          <Plus className="w-4 h-4" />
          Connect a Repository
          <ExternalLink className="w-3.5 h-3.5 opacity-75" />
        </motion.a>
      )}
    </motion.div>
  );
}
