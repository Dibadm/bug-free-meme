import type { ReactNode } from "react";

interface TopNavProps {
  title: string;
  rightAction?: ReactNode;
  onBack?: () => void;
  className?: string;
}

export function TopNav({ title, rightAction, onBack, className = "" }: TopNavProps) {
  return (
    <header className={`sticky top-0 z-30 bg-habesha-dark/80 backdrop-blur-xl border-b border-white/5 ${className}`}>
      <div className="max-w-lg mx-auto flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          {onBack && (
            <button
              onClick={onBack}
              className="p-2 -ml-2 rounded-xl hover:bg-white/5 transition-colors"
            >
              <svg className="h-5 w-5 text-white/70" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M15 18l-6-6 6-6" />
              </svg>
            </button>
          )}
          <h1 className="text-lg font-semibold text-white">{title}</h1>
        </div>
        {rightAction && <div className="flex items-center gap-2">{rightAction}</div>}
      </div>
    </header>
  );
}
