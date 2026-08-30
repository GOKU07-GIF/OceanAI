import { ButtonHTMLAttributes, ReactNode } from "react";

type Variant =
  | "primary"
  | "secondary"
  | "outline"
  | "ghost";

interface OceanButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: Variant;
  className?: string;
}

const variants: Record<Variant, string> = {
  primary:
    "bg-cyan-500 text-white hover:bg-cyan-600 shadow-lg shadow-cyan-500/30",

  secondary:
    "bg-slate-800 text-white hover:bg-slate-700",

  outline:
    "border border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-slate-950",

  ghost:
    "text-cyan-400 hover:bg-cyan-400/10",
};

export default function OceanButton({
  children,
  variant = "primary",
  className = "",
  ...props
}: OceanButtonProps): React.JSX.Element {
  return (
    <button
      className={`
        rounded-xl
        px-6
        py-3
        font-semibold
        transition-all
        duration-300
        hover:-translate-y-1
        ${variants[variant]}
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
}