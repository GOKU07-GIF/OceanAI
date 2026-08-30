import { motion } from "framer-motion";
import { Link } from "react-router-dom";

export default function HeroContent(): React.JSX.Element {
  return (
    <motion.div
      initial={{ opacity: 0, x: -80 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.8 }}
      className="max-w-3xl"
    >
      <p className="mb-4 font-semibold uppercase tracking-widest text-cyan-400">
        Ocean Intelligence Platform
      </p>

      <h1 className="text-5xl font-extrabold leading-tight text-white md:text-7xl">
        AI Powered
        <span className="block text-cyan-400">
          Ocean Monitoring
        </span>
      </h1>

      <p className="mt-8 max-w-2xl text-lg leading-8 text-slate-300">
        OceanAI helps researchers and organizations monitor
        ocean health using Artificial Intelligence, satellite
        data, IoT sensors, and predictive analytics.
      </p>

      <div className="mt-10 flex flex-wrap gap-4">
        <Link
          to="/login"
          className="rounded-xl bg-cyan-500 px-8 py-4 font-semibold text-white transition hover:bg-cyan-600"
        >
          Get Started
        </Link>

        <Link
          to="/dashboard"
          className="rounded-xl border border-cyan-500 px-8 py-4 font-semibold text-cyan-400 transition hover:bg-cyan-500 hover:text-white"
        >
          View Dashboard
        </Link>
      </div>
    </motion.div>
  );
}