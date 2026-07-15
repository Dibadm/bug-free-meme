import type { ReactNode } from "react";
import { createContext } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";

interface ModalContextValue {
  close: () => void;
}

const ModalContext = createContext<ModalContextValue | null>(null);

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: "sm" | "md" | "lg";
}

const sizeClasses = {
  sm: "max-w-sm",
  md: "max-w-md",
  lg: "max-w-lg",
};

export function Modal({ isOpen, onClose, title, children, size = "md" }: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <ModalContext.Provider value={{ close: onClose }}>
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={onClose}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className={`relative w-full ${sizeClasses[size]} bg-habesha-surface border border-white/10 rounded-3xl shadow-2xl`}
            >
              {(title || onClose !== undefined) && (
                <div className="flex items-center justify-between p-5 border-b border-white/5">
                  {title && <h2 className="text-lg font-semibold">{title}</h2>}
                  <button onClick={onClose} className="p-1 rounded-lg hover:bg-white/5 transition-colors">
                    <X className="h-5 w-5 text-white/60" />
                  </button>
                </div>
              )}
              <div className="p-5">{children}</div>
            </motion.div>
          </div>
        </ModalContext.Provider>
      )}
    </AnimatePresence>
  );
}
