import { motion } from "framer-motion";

interface LiveBallProps {
  number: number;
  size?: "sm" | "md" | "lg";
  isNew?: boolean;
  className?: string;
}

const sizeClasses = {
  sm: "h-10 w-10 text-sm",
  md: "h-14 w-14 text-base",
  lg: "h-20 w-20 text-xl",
};

export function LiveBall({ number, size = "md", isNew = false, className = "" }: LiveBallProps) {
  return (
    <motion.div
      initial={isNew ? { scale: 0, rotate: -180 } : false}
      animate={isNew ? { scale: 1, rotate: 0 } : undefined}
      transition={isNew ? { type: "spring", stiffness: 260, damping: 20 } : undefined}
      className={[
        "relative flex items-center justify-center rounded-full bg-gradient-to-br from-habesha-gold to-habesha-gold-dark text-habesha-dark font-bold shadow-lg shadow-habesha-gold/30",
        sizeClasses[size],
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <span className="relative z-10">{number}</span>
      <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/20 to-transparent pointer-events-none" />
    </motion.div>
  );
}
