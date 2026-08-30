import { ReactNode } from "react";

interface OceanModalProps {
  open: boolean;
  title: string;
  children: ReactNode;
  onClose: () => void;
}

export default function OceanModal({
  open,
  title,
  children,
  onClose,
}: OceanModalProps): React.JSX.Element {
  if (!open) return <></>;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-2xl bg-slate-900 p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">
            {title}
          </h2>

          <button
            onClick={onClose}
            className="text-2xl text-slate-400 hover:text-white"
          >
            ×
          </button>
        </div>

        <div>{children}</div>
      </div>
    </div>
  );
}