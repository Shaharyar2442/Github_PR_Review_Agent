"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const PHASES = [
  "Fetching pending reviews...",
  "Scanning repositories...",
  "Running AI analysis...",
  "Searching for pending errors...",
  "Analyzing PR diffs...",
  "Checking for security issues...",
];

export default function LoadingState() {
  const [phaseIndex, setPhaseIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPhaseIndex((i) => (i + 1) % PHASES.length);
    }, 1800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-24 gap-8">
      {/* Neural pulse rings */}
      <div className="relative flex items-center justify-center w-20 h-20">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="absolute rounded-full border-2 border-red-primary/60 animate-ping"
            style={{
              width: `${(i + 1) * 28}px`,
              height: `${(i + 1) * 28}px`,
              animationDelay: `${i * 0.3}s`,
              animationDuration: "1.5s",
            }}
          />
        ))}
        {/* Core dot */}
        <div className="w-5 h-5 rounded-full bg-red-primary shadow-[0_0_12px_3px_rgba(220,20,60,0.5)]" />
      </div>

      {/* Cycling text */}
      <div className="h-7 flex items-center">
        <AnimatePresence mode="wait">
          <motion.p
            key={phaseIndex}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
            className="text-sm font-medium text-text-secondary tracking-wide"
          >
            {PHASES[phaseIndex]}
          </motion.p>
        </AnimatePresence>
      </div>

      {/* Skeleton cards */}
      <div className="w-full max-w-3xl grid gap-4">
        {[1, 2].map((i) => (
          <div
            key={i}
            className="h-40 rounded-2xl bg-surface-2 border border-border overflow-hidden relative"
          >
            <div
              className="absolute inset-0 -translate-x-full animate-[shimmer_1.8s_infinite]"
              style={{
                background:
                  "linear-gradient(90deg, transparent, rgba(220,20,60,0.04), transparent)",
              }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
