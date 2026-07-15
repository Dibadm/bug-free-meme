interface AvatarProps {
  src?: string | null;
  alt?: string;
  fallback?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeClasses: Record<string, string> = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-14 w-14 text-lg",
};

export function Avatar({ src, alt, fallback, size = "md", className = "" }: AvatarProps) {
  const initial = (fallback || alt || "?")?.[0]?.toUpperCase() || "?";

  return (
    <div
      className={[
        "rounded-full bg-habesha-surface-light border border-white/10 flex items-center justify-center overflow-hidden shrink-0",
        sizeClasses[size],
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {src ? (
        <img src={src} alt={alt || "Avatar"} className="h-full w-full object-cover" />
      ) : (
        <span className="text-white/70 font-semibold">{initial}</span>
      )}
    </div>
  );
}
