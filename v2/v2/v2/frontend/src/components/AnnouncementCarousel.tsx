import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Badge } from "./Badge";
import { Megaphone } from "lucide-react";

interface Announcement {
  id: string;
  title: string;
  message: string;
  type?: "info" | "warning" | "success" | "promotion";
}

interface AnnouncementCarouselProps {
  announcements: Announcement[];
  autoAdvanceInterval?: number;
  className?: string;
}

export function AnnouncementCarousel({
  announcements,
  autoAdvanceInterval = 5000,
  className = "",
}: AnnouncementCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (announcements.length <= 1) return;
    intervalRef.current = window.setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % announcements.length);
    }, autoAdvanceInterval);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [announcements.length, autoAdvanceInterval]);

  if (announcements.length === 0) return null;

  const current = announcements[currentIndex];

  const variantColors: Record<string, string> = {
    info: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    warning: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    success: "bg-green-500/20 text-green-400 border-green-500/30",
    promotion: "bg-habesha-gold/20 text-habesha-gold border-habesha-gold/30",
  };

  return (
    <div className={`relative overflow-hidden bg-habesha-surface/80 backdrop-blur-xl border border-white/10 rounded-3xl ${className}`}>
      <div className="flex items-center gap-3 p-4">
        <div className="shrink-0">
          <Megaphone className="h-5 w-5 text-habesha-gold" />
        </div>
        <div className="flex-1 min-w-0">
          <AnimatePresence mode="wait">
            <motion.div
              key={current.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-0.5"
            >
              <p className="text-sm font-semibold text-white truncate">{current.title}</p>
              <p className="text-xs text-white/60 truncate">{current.message}</p>
            </motion.div>
          </AnimatePresence>
        </div>
        {current.type && (
          <Badge variant="default" className={variantColors[current.type] || variantColors.info}>
            {current.type}
          </Badge>
        )}
      </div>

      {announcements.length > 1 && (
        <div className="flex items-center justify-center gap-1.5 pb-3">
          {announcements.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentIndex(idx)}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                idx === currentIndex ? "w-4 bg-habesha-gold" : "w-1.5 bg-white/20"
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
