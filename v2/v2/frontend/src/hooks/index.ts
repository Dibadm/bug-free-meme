import { useState, useEffect } from "react";
import { useTelegram } from "@/lib/telegram";

export function useCountdown(end: Date | number, onComplete?: () => void) {
  const [seconds, setSeconds] = useState(() => {
    const total = typeof end === "number" ? end - Date.now() : end.getTime() - Date.now();
    return Math.max(0, Math.floor(total / 1000));
  });

  useEffect(() => {
    if (seconds <= 0) {
      onComplete?.();
      return;
    }
    const tick = setInterval(() => {
      setSeconds((s) => {
        if (s <= 1) {
          clearInterval(tick);
          onComplete?.();
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(tick);
  }, [seconds, onComplete]);

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  return { seconds, minutes, remainingSeconds, isComplete: seconds <= 0 };
}

export function useHaptics() {
  const { haptic } = useTelegram();

  return {
    light: () => haptic.impact("light"),
    medium: () => haptic.impact("medium"),
    heavy: () => haptic.impact("heavy"),
    success: () => haptic.notification("success"),
    error: () => haptic.notification("error"),
    warning: () => haptic.notification("warning"),
  };
}

export { useWebSocket } from "./useWebSocket";
