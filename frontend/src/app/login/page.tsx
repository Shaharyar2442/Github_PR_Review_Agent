"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Lock, User, ArrowRight, AlertCircle, GitPullRequest, Bot, ShieldCheck } from "lucide-react";
import Logo from "../components/Logo";

const FEATURES = [
  {
    icon: <Bot className="w-4 h-4" />,
    text: "AI analyzes every PR diff automatically",
  },
  {
    icon: <ShieldCheck className="w-4 h-4" />,
    text: "Catches bugs & security issues instantly",
  },
  {
    icon: <GitPullRequest className="w-4 h-4" />,
    text: "Posts review comments directly to GitHub",
  },
];

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const body = new URLSearchParams();
      body.append("username", username);
      body.append("password", password);
      const res = await fetch(`${apiUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      if (!res.ok) throw new Error("Invalid username or password.");
      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      router.push("/");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* ── Left brand panel ── */}
      <div className="hidden lg:flex lg:w-1/2 auth-brand-panel flex-col justify-between p-12 relative overflow-hidden">
        {/* Background glow */}
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-red-primary/10 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-72 h-72 rounded-full bg-red-deep/5 blur-3xl pointer-events-none" />

        {/* Logo */}
        <div className="flex items-center gap-3 relative z-10">
          <Logo size={38} />
          <span className="text-white font-bold text-xl tracking-tight">ReviewBot</span>
        </div>

        {/* Hero */}
        <div className="relative z-10 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <h1 className="text-4xl font-extrabold text-white leading-tight mb-4">
              Your AI-powered<br />
              <span className="text-red-primary">code review</span> agent.
            </h1>
            <p className="text-zinc-400 text-base leading-relaxed max-w-xs">
              Every pull request, reviewed by AI in seconds. Catch what humans miss.
            </p>
          </motion.div>

          <ul className="space-y-3">
            {FEATURES.map((f, i) => (
              <motion.li
                key={i}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.35 + i * 0.1, duration: 0.45 }}
                className="flex items-center gap-3 text-zinc-300 text-sm"
              >
                <span className="flex-shrink-0 w-7 h-7 rounded-lg bg-red-primary/15 border border-red-primary/30 flex items-center justify-center text-red-primary">
                  {f.icon}
                </span>
                {f.text}
              </motion.li>
            ))}
          </ul>
        </div>

        {/* Bottom quote */}
        <p className="text-zinc-600 text-xs relative z-10">
          Trusted by developers who ship fast.
        </p>
      </div>

      {/* ── Right form panel ── */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 bg-surface">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-sm"
        >
          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-2 mb-8 justify-center">
            <Logo size={32} />
            <span className="font-bold text-lg text-text-primary">ReviewBot</span>
          </div>

          <h2 className="text-2xl font-bold text-text-primary mb-1">Welcome back</h2>
          <p className="text-text-secondary text-sm mb-8">
            Sign in to manage your pending reviews.
          </p>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.97, y: -4 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.97 }}
                className="mb-5 p-3.5 rounded-xl bg-red-muted border border-red-primary/20 text-red-primary text-sm flex items-center gap-2"
              >
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Username */}
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1.5 uppercase tracking-widest">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  id="login-username"
                  type="text"
                  required
                  autoComplete="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="johndoe"
                  className="w-full pl-10 pr-4 py-3 rounded-xl text-sm bg-surface-2 border border-border text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-red-primary/30 focus:border-red-primary transition-all"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1.5 uppercase tracking-widest">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  id="login-password"
                  type="password"
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-3 rounded-xl text-sm bg-surface-2 border border-border text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-red-primary/30 focus:border-red-primary transition-all"
                />
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.015 }}
              whileTap={{ scale: 0.985 }}
              id="login-submit"
              type="submit"
              disabled={loading}
              className="w-full mt-2 flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-semibold text-sm text-white bg-red-primary hover:bg-red-deep shadow-lg shadow-red-primary/25 hover:shadow-red-primary/40 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  Sign in
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </motion.button>
          </form>

          <p className="mt-6 text-center text-sm text-text-secondary">
            Don&apos;t have an account?{" "}
            <button
              id="goto-register"
              onClick={() => router.push("/register")}
              className="text-red-primary font-semibold hover:text-red-deep transition-colors"
            >
              Create account
            </button>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
