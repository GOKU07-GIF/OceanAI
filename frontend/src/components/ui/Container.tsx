import { ReactNode } from "react";

interface ContainerProps {
  children: ReactNode;
}

export default function Container({
  children,
}: ContainerProps): React.JSX.Element {
  return (
    <div className="mx-auto max-w-7xl px-6">
      {children}
    </div>
  );
}