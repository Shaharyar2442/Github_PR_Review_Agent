"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Lock, User, AtSign, ArrowRight, AlertCircle, Zap, Star, GitMerge } from "lucide-react";
import Logo from "../components/Logo";

const PERKS = [
  { icon: <Zap className="w-4 h-4" />, text: "Instant AI review on every PR" },
  { icon: <Star className="w-4 h-4" />, text: "Prioritized issue detection" },
  { icon: <GitMerge className="w-4 h-4" />, text: "Human-in-the-loop approval flow" },
];

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [githubUsername, setGithubUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

      const res = await fetch(`${apiUrl}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, github_username: githubUsername, password }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Registration failed.");
      }

      // Auto-login after register
      const loginBody = new URLSearchParams();
      loginBody.append("username", username);
      loginBody.append("password", password);
      const loginRes = await fetch(`${apiUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: loginBody,
      });
      if (!loginRes.ok) throw new Error("Account created! Please sign in manually.");
      const data = await loginRes.json();
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
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 rounded-full bg-red-primary/10 blur-3xl pointer-events-none" />

        <div className="flex items-center gap-3 relative z-10">
          <Logo size={38} />
          <span className="text-white font-bold text-xl tracking-tight">ReviewBot</span>
        </div>

        <div className="relative z-10 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <h1 className="text-4xl font-extrabold text-white leading-tight mb-4">
              Smarter reviews.<br />
              <span className="text-red-primary">Faster shipping.</span>
            </h1>
            <p className="text-zinc-400 text-base leading-relaxed max-w-xs">
              Join developers who automate code quality with AI. Free to get started.
            </p>
          </motion.div>

          <ul className="space-y-3">
            {PERKS.map((p, i) => (
              <motion.li
                key={i}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.35 + i * 0.1 }}
                className="flex items-center gap-3 text-zinc-300 text-sm"
              >
                <span className="flex-shrink-0 w-7 h-7 rounded-lg bg-red-primary/15 border border-red-primary/30 flex items-center justify-center text-red-primary">
                  {p.icon}
                </span>
                {p.text}
              </motion.li>
            ))}
          </ul>
        </div>

        <p className="text-zinc-600 text-xs relative z-10">
          No credit card required. Install on GitHub in seconds.
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
          <div className="flex lg:hidden items-center gap-2 mb-8 justify-center">
            <Logo size={32} />
            <span className="font-bold text-lg text-text-primary">ReviewBot</span>
          </div>

          <h2 className="text-2xl font-bold text-text-primary mb-1">Create your account</h2>
          <p className="text-text-secondary text-sm mb-8">
            Get AI-powered reviews on every pull request.
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

          <form onSubmit={handleRegister} className="space-y-4">
            {/* Username */}
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1.5 uppercase tracking-widest">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  id="register-username"
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="johndoe"
                  className="w-full pl-10 pr-4 py-3 rounded-xl text-sm bg-surface-2 border border-border text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-red-primary/30 focus:border-red-primary transition-all"
                />
              </div>
            </div>

            {/* GitHub Username */}
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1.5 uppercase tracking-widest">
                GitHub Username
              </label>
              <div className="relative">
                <AtSign className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  id="register-github-username"
                  type="text"
                  required
                  value={githubUsername}
                  onChange={(e) => setGithubUsername(e.target.value)}
                  placeholder="your-github-handle"
                  className="w-full pl-10 pr-4 py-3 rounded-xl text-sm bg-surface-2 border border-border text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-red-primary/30 focus:border-red-primary transition-all"
                />
              </div>
              <p className="text-xs text-text-muted mt-1.5">
                Must match your exact GitHub handle — this links your PRs to your account.
              </p>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1.5 uppercase tracking-widest">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  id="register-password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min. 8 characters"
                  className="w-full pl-10 pr-4 py-3 rounded-xl text-sm bg-surface-2 border border-border text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-red-primary/30 focus:border-red-primary transition-all"
                />
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.015 }}
              whileTap={{ scale: 0.985 }}
              id="register-submit"
              type="submit"
              disabled={loading}
              className="w-full mt-2 flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-semibold text-sm text-white bg-red-primary hover:bg-red-deep shadow-lg shadow-red-primary/25 hover:shadow-red-primary/40 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  Creating account...
                </>
              ) : (
                <>
                  Create account
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </motion.button>
          </form>

          <p className="mt-6 text-center text-sm text-text-secondary">
            Already have an account?{" "}
            <button
              id="goto-login"
              onClick={() => router.push("/login")}
              className="text-red-primary font-semibold hover:text-red-deep transition-colors"
            >
              Sign in
            </button>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
