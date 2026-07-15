import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp } from "lucide-react";
import { CountUp } from "./CountUp";

interface BalanceCardProps {
  balance: number;
  bonus?: number;
  jackpot?: number;
  currency?: string;
  className?: string;
}

export function BalanceCard({
  balance,
  bonus = 0,
  jackpot = 0,
  currency = "ETB",
  className = "",
}: BalanceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <motion.div
      whileTap={{ scale: 0.98 }}
      onClick={() => setIsExpanded(!isExpanded)}
      className={[
        "relative overflow-hidden bg-habesha-surface/80 backdrop-blur-xl border border-white/10 rounded-3xl p-5 cursor-pointer",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-habesha-gold/10 to-transparent pointer-events-none" />
      <div className="relative z-10">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-white/60 uppercase tracking-wider">Balance</p>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-bold text-white">
              {currency}<CountUp end={balance} />
            </span>
          </div>
          </div>
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
            className="text-white/40"
          >
            {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
          </motion.div>
        </div>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="mt-4 pt-4 border-t border-white/10 space-y-2"
            >
              {bonus > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-white/60">Bonus</span>
                  <span className="text-sm font-semibold text-habesha-gold">
                    +{currency} {bonus.toFixed(2)}
                  </span>
                </div>
              )}
              {jackpot > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-white/60">Jackpot</span>
                  <span className="text-sm font-semibold text-habesha-green">
                    {currency} {jackpot.toFixed(2)}
                  </span>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
