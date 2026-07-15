import type { ReactNode } from "react";
import { motion } from "framer-motion";

interface CardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  hover?: boolean;
}

export function Card({ children, className = "", onClick, hover = false }: CardProps) {
  return (
    <motion.div
      whileTap={onClick ? { scale: 0.98 } : undefined}
      className={[
        "bg-habesha-surface/80 backdrop-blur-xl border border-white/10 rounded-3xl",
        hover && "transition-all duration-200 active:scale-[0.98]",
        onClick && "cursor-pointer",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      onClick={onClick}
    >
      {children}
    </motion.div>
  );
}
