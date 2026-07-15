import { useEffect, useState } from "react";

interface CountdownProps {
  end: Date | number;
  onComplete?: () => void;
  className?: string;
}

export function Countdown({ end, onComplete, className = "" }: CountdownProps) {
  const calculate = () => {
    const total = typeof end === "number" ? end - Date.now() : end.getTime() - Date.now();
    if (total <= 0) return { seconds: 0, minutes: 0, hours: 0, total: 0 };
    return {
      total,
      seconds: Math.floor((total / 1000) % 60),
      minutes: Math.floor((total / (1000 * 60)) % 60),
      hours: Math.floor(total / (1000 * 60 * 60)),
    };
  };

  const [time, setTime] = useState(calculate);

  useEffect(() => {
    if (time.total <= 0) {
      onComplete?.();
      return;
    }
    const tick = setInterval(() => setTime(calculate()), 1000);
    return () => clearInterval(tick);
  }, [time.total, onComplete]);

  const pad = (n: number) => String(n).padStart(2, "0");

  return (
    <div className={`flex items-center gap-1 font-mono text-sm ${className}`}>
      <span className="bg-habesha-surface-light px-2 py-1 rounded-lg text-white">{pad(time.hours)}</span>
      <span className="text-white/40">:</span>
      <span className="bg-habesha-surface-light px-2 py-1 rounded-lg text-white">{pad(time.minutes)}</span>
      <span className="text-white/40">:</span>
      <span className="bg-habesha-surface-light px-2 py-1 rounded-lg text-habesha-gold">{pad(time.seconds)}</span>
    </div>
  );
}
