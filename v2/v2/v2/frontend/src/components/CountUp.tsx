import { useEffect, useRef, useState } from "react";

interface CountUpProps {
  end: number;
  duration?: number;
  start?: number;
}

export function CountUp({ end, duration = 1000, start = 0 }: CountUpProps) {
  const [value, setValue] = useState(start);
  const ref = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);

  useEffect(() => {
    startTimeRef.current = performance.now();
    const animate = (now: number) => {
      const elapsed = now - (startTimeRef.current ?? now);
      const progress = Math.min(elapsed / duration, 1);
      const current = Math.floor(start + (end - start) * easeOutCubic(progress));
      setValue(current);
      if (progress < 1) {
        ref.current = requestAnimationFrame(animate);
      }
    };
    ref.current = requestAnimationFrame(animate);
    return () => {
      if (ref.current) cancelAnimationFrame(ref.current);
    };
  }, [end, duration, start]);

  return <>{value.toLocaleString()}</>;
}

function easeOutCubic(t: number) {
  return 1 - Math.pow(1 - t, 3);
}
