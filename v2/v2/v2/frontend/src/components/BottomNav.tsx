import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { Home, Wallet, User } from "lucide-react";

interface BottomNavProps {
  active: string;
  onNavigate: (path: string) => void;
  items?: { id: string; label: string; icon: ReactNode }[];
}

const defaultItems = [
  { id: "home", label: "Home", icon: <Home className="h-5 w-5" /> },
  { id: "wallet", label: "Wallet", icon: <Wallet className="h-5 w-5" /> },
  { id: "profile", label: "Profile", icon: <User className="h-5 w-5" /> },
];

export function BottomNav({ active, onNavigate, items = defaultItems }: BottomNavProps) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-habesha-surface/90 backdrop-blur-xl border-t border-white/5 safe-area-inset-bottom">
      <div className="max-w-lg mx-auto flex items-center justify-around py-2">
        {items.map((item) => {
          const isActive = active === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`flex flex-col items-center gap-0.5 p-2 rounded-xl transition-colors duration-200 min-w-[64px] ${
                isActive ? "text-habesha-gold" : "text-white/40"
              }`}
            >
              {item.icon}
              <span className="text-[10px] font-medium">{item.label}</span>
              {isActive && (
                <motion.div
                  layoutId="bottomNavIndicator"
                  className="absolute -top-2 w-8 h-0.5 bg-habesha-gold rounded-full"
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
