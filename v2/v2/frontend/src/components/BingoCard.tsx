import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface BingoCardProps {
  numbers: number[];
  calledNumbers: number[];
  markedNumbers: number[];
  winningPattern?: string;
  size?: "sm" | "md" | "lg";
  onNumberClick?: (index: number, number: number) => void;
  className?: string;
}

const sizeClasses = {
  sm: "gap-1 p-2",
  md: "gap-1.5 p-3",
  lg: "gap-2 p-4",
};

const cellSizeClasses = {
  sm: "h-10 text-sm",
  md: "h-12 text-base",
  lg: "h-14 text-lg",
};

export function BingoCard({
  numbers,
  calledNumbers,
  markedNumbers,
  winningPattern,
  size = "md",
  onNumberClick,
  className = "",
}: BingoCardProps) {
  const [flashIndex, setFlashIndex] = useState<number | null>(null);

  useEffect(() => {
    if (markedNumbers.length > 0) {
      const lastMarked = markedNumbers[markedNumbers.length - 1];
      const idx = numbers.indexOf(lastMarked);
      if (idx >= 0) {
        setFlashIndex(idx);
        const t = setTimeout(() => setFlashIndex(null), 600);
        return () => clearTimeout(t);
      }
    }
  }, [markedNumbers, numbers]);

  const calledSet = new Set(calledNumbers);
  const markedSet = new Set(markedNumbers);

  return (
    <div className={["grid grid-cols-5 bg-habesha-surface/80 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden", sizeClasses[size], className]
      .filter(Boolean)
      .join(" ")}>
      {numbers.map((num, idx) => {
        const isCalled = calledSet.has(num);
        const isMarked = markedSet.has(num);
        const isFlashing = flashIndex === idx;
        const isWinningCell = winningPattern && isMarked;

        return (
          <motion.button
            key={idx}
            onClick={() => onNumberClick?.(idx, num)}
            animate={
              isFlashing
                ? { scale: [1, 1.15, 1], backgroundColor: ["rgba(255,215,0,0.3)", "rgba(255,215,0,0.6)", "rgba(255,215,0,0.3)"] }
                : isWinningCell
                  ? { boxShadow: ["0 0 0 rgba(0,208,132,0)", "0 0 20px rgba(0,208,132,0.6)", "0 0 0 rgba(0,208,132,0)"] }
                  : undefined
            }
            transition={{ duration: 0.4 }}
            className={[
              "flex items-center justify-center rounded-2xl font-semibold transition-all duration-300",
              cellSizeClasses[size],
              isMarked
                ? "bg-habesha-gold/20 text-habesha-gold border border-habesha-gold/40 shadow-lg shadow-habesha-gold/10"
                : isCalled
                  ? "bg-habesha-surface-light/50 text-white/30 border border-white/5"
                  : "bg-habesha-surface-light text-white/90 border border-white/10 hover:border-white/20",
              onNumberClick && "cursor-pointer active:scale-95",
            ]
              .filter(Boolean)
              .join(" ")}
          >
            {num === 0 ? (
              <span className="text-habesha-gold/60 text-lg">FREE</span>
            ) : (
              <span className={isMarked ? "text-habesha-gold" : isCalled ? "text-white/30" : ""}>
                {num}
              </span>
            )}
          </motion.button>
        );
      })}
    </div>
  );
}
