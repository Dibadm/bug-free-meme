import { CountUp } from "./CountUp";

interface StatCardProps {
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
  trend?: number;
  className?: string;
}

export function StatCard({ label, value, prefix = "", suffix = "", trend, className = "" }: StatCardProps) {
  return (
    <div className={`bg-habesha-surface/80 border border-white/10 rounded-2xl p-4 ${className}`}>
      <p className="text-sm text-white/60 mb-1">{label}</p>
      <div className="flex items-baseline gap-2">
        <span className="text-xl font-bold text-white">
          {prefix}
          <CountUp end={value} />
          {suffix}
        </span>
        {trend !== undefined && (
          <span className={`text-xs font-medium ${trend >= 0 ? "text-green-400" : "text-red-400"}`}>
            {trend >= 0 ? "+" : ""}{trend}%
          </span>
        )}
      </div>
    </div>
  );
}
