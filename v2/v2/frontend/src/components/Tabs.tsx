import { motion } from "framer-motion";

interface TabsProps {
  tabs: { id: string; label: string; icon?: React.ReactNode }[];
  activeTab: string;
  onChange: (id: string) => void;
  variant?: "default" | "pills";
  className?: string;
}

export function Tabs({ tabs, activeTab, onChange, variant = "default", className = "" }: TabsProps) {
  return (
    <div className={`relative ${className}`}>
      <div className={`flex items-center gap-1 p-1 bg-habesha-surface-light/50 rounded-2xl ${variant === "pills" ? "" : "border border-white/10"}`}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onChange(tab.id)}
              className={[
                "relative flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-medium transition-colors duration-200 flex-1",
                isActive ? "text-white" : "text-white/60 hover:text-white/80",
              ]
                .filter(Boolean)
                .join(" ")}
            >
              {isActive && (
                <motion.div
                  layoutId="tabIndicator"
                  className="absolute inset-0 bg-habesha-surface rounded-xl shadow-lg"
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
              <span className="relative z-10 flex items-center gap-1.5">
                {tab.icon}
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
