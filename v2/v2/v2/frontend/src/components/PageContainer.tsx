import type { ReactNode } from "react";

interface PageContainerProps {
  children: ReactNode;
  withNav?: boolean;
  className?: string;
}

export function PageContainer({ children, withNav = true, className = "" }: PageContainerProps) {
  return (
    <div className={`min-h-screen bg-habesha-dark ${withNav ? "pb-24" : ""} ${className}`}>
      <div className="max-w-lg mx-auto">{children}</div>
    </div>
  );
}
