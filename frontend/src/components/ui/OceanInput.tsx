import { InputHTMLAttributes } from "react";

interface OceanInputProps
  extends InputHTMLAttributes<HTMLInputElement> {
  className?: string;
}

export default function OceanInput({
  className = "",
  ...props
}: OceanInputProps): React.JSX.Element {
  return (
    <input
      className={`
        w-full
        rounded-xl
        border
        border-slate-700
        bg-slate-900
        px-5
        py-3
        text-white
        outline-none
        transition-all
        duration-300
        focus:border-cyan-400
        ${className}
      `}
      {...props}
    />
  );
}