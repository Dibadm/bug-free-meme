interface SkeletonProps {
  className?: string;
  variant?: "text" | "circular" | "rectangular";
}

const variantClasses: Record<string, string> = {
  text: "rounded",
  circular: "rounded-full",
  rectangular: "rounded-2xl",
};

export function Skeleton({ className = "", variant = "rectangular" }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse bg-habesha-surface-light/50 ${variantClasses[variant]} ${className}`}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-habesha-surface/80 border border-white/10 rounded-3xl p-5 space-y-4">
      <Skeleton className="h-5 w-3/4" variant="text" />
      <Skeleton className="h-4 w-1/2" variant="text" />
      <Skeleton className="h-10 w-full" variant="rectangular" />
    </div>
  );
}

export function StatCardSkeleton() {
  return (
    <div className="bg-habesha-surface/80 border border-white/10 rounded-2xl p-4 space-y-2">
      <Skeleton className="h-4 w-1/2" variant="text" />
      <Skeleton className="h-6 w-3/4" variant="text" />
    </div>
  );
}
