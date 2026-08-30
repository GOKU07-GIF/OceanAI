import { motion } from "framer-motion";

export default function ScrollIndicator(): React.JSX.Element {
  return (
    <motion.div
      animate={{
        y: [0, 10, 0],
      }}
      transition={{
        repeat: Infinity,
        duration: 1.8,
      }}
      className="absolute bottom-10 left-1/2 -translate-x-1/2 text-cyan-400 text-3xl"
    >
      ↓
    </motion.div>
  );
}