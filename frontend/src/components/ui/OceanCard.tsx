import { ReactNode } from "react";

interface OceanCardProps {
  children: ReactNode;
  className?: string;
}

export default function OceanCard({
  children,
  className = "",
}: OceanCardProps): React.JSX.Element {
  return (
    <div
      className={`
        rounded-3xl
        border
        border-slate-800
        bg-slate-900/70
        p-8
        backdrop-blur-xl
        transition-all
        duration-300
        hover:border-cyan-500
        hover:shadow-xl
        hover:shadow-cyan-500/20
        ${className}
      `}
    >
      {children}
    </div>
  );
}