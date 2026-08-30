import { ReactNode } from "react";

interface OceanBadgeProps {
  children: ReactNode;
  className?: string;
}

export default function OceanBadge({
  children,
  className = "",
}: OceanBadgeProps): React.JSX.Element {
  return (
    <span
      className={`
        inline-flex
        items-center
        rounded-full
        bg-cyan-500/20
        px-4
        py-2
        text-sm
        font-semibold
        text-cyan-400
        ${className}
      `}
    >
      {children}
    </span>
  );
}