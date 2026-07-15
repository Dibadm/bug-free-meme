import { motion } from "framer-motion";

interface LoadingProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeClasses = {
  sm: "h-5 w-5 border-2",
  md: "h-8 w-8 border-2",
  lg: "h-12 w-12 border-3",
};

export function Loading({ size = "md", className = "" }: LoadingProps) {
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.8, ease: "linear" }}
        className={[
          "rounded-full border-habesha-gold border-t-transparent",
          sizeClasses[size],
        ]
          .filter(Boolean)
          .join(" ")}
      />
    </div>
  );
}

interface SpinnerProps {
  text?: string;
}

export function Spinner({ text }: SpinnerProps) {
  return (
    <div className="flex flex-col items-center gap-3">
      <Loading size="lg" />
      {text && <p className="text-white/60 text-sm">{text}</p>}
    </div>
  );
}
