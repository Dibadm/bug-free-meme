import type { InputHTMLAttributes, ReactNode } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: ReactNode;
}

export function Input({ label, error, icon, className = "", ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && <label className="block text-sm font-medium text-white/70 mb-2">{label}</label>}
      <div className="relative">
        {icon && <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">{icon}</span>}
        <input
          className={[
            "w-full px-4 py-3 bg-habesha-surface-light border rounded-xl text-white",
            "placeholder-white/40 focus:outline-none focus:border-habesha-gold/50 transition-colors duration-200",
            error ? "border-red-500/50" : "border-white/10",
            icon && "pl-11",
            className,
          ]
            .filter(Boolean)
            .join(" ")}
          {...props}
        />
      </div>
      {error && <p className="mt-1.5 text-sm text-red-400">{error}</p>}
    </div>
  );
}
