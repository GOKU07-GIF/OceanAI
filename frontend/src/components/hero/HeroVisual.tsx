import { motion } from "framer-motion";

export default function HeroVisual(): React.JSX.Element {
  return (
    <motion.div
      initial={{ opacity: 0, x: 80 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 1 }}
      className="flex items-center justify-center"
    >
      <div className="relative flex h-96 w-96 items-center justify-center rounded-full border border-cyan-400/30 bg-cyan-500/10 shadow-2xl shadow-cyan-500/20">

        {/* Outer Glow */}
        <div className="absolute h-[420px] w-[420px] animate-pulse rounded-full border border-cyan-500/20" />

        {/* Earth */}
        <span className="text-8xl select-none">
          🌍
        </span>

      </div>
    </motion.div>
  );
}