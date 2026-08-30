export default function AnimatedBackground(): React.JSX.Element {
  return (
    <>
      {/* Center Glow */}
      <div className="absolute left-1/2 top-1/2 h-[800px] w-[800px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/20 blur-[180px]" />

      {/* Top Right Glow */}
      <div className="absolute right-0 top-0 h-[500px] w-[500px] rounded-full bg-blue-500/10 blur-[150px]" />

      {/* Bottom Left Glow */}
      <div className="absolute bottom-0 left-0 h-[500px] w-[500px] rounded-full bg-sky-500/10 blur-[150px]" />
    </>
  );
}