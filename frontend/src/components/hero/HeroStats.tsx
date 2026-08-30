import { motion } from "framer-motion";

interface HeroStat {
  number: string;
  label: string;
}

const stats: HeroStat[] = [
  {
    number: "98%",
    label: "Prediction Accuracy",
  },
  {
    number: "24/7",
    label: "Live Monitoring",
  },
  {
    number: "5000+",
    label: "Ocean Samples",
  },
  {
    number: "40+",
    label: "Research Areas",
  },
];

export default function HeroStats(): React.JSX.Element {
  return (
    <motion.div
      initial={{ opacity: 0, y: 80 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.2 }}
      className="mt-20 grid grid-cols-2 gap-8 md:grid-cols-4"
    >
      {stats.map((item) => (
        <div
          key={item.label}
          className="rounded-xl border border-slate-700 bg-slate-900/60 p-6 text-center backdrop-blur-sm"
        >
          <h2 className="text-4xl font-bold text-cyan-400">
            {item.number}
          </h2>

          <p className="mt-2 text-slate-400">
            {item.label}
          </p>
        </div>
      ))}
    </motion.div>
  );
}