import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { AnimatePresence } from "framer-motion";
import { X } from "lucide-react";

interface SheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
  title?: string;
  side?: "bottom" | "top";
}

export function Sheet({ isOpen, onClose, children, title }: SheetProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="relative w-full max-h-[85vh] bg-habesha-surface border-t sm:border border-white/10 sm:rounded-3xl rounded-t-3xl shadow-2xl overflow-hidden"
          >
            {title && (
              <div className="flex items-center justify-between p-5 border-b border-white/5">
                <h2 className="text-lg font-semibold">{title}</h2>
                <button onClick={onClose} className="p-1 rounded-lg hover:bg-white/5 transition-colors">
                  <X className="h-5 w-5 text-white/60" />
                </button>
              </div>
            )}
            <div className="p-5 overflow-y-auto">{children}</div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
