import { motion } from "framer-motion";

import { OceanButton, Container } from "../ui";

import AnimatedBackground from "./AnimatedBackground";
import HeroStats from "./HeroStats";
import ScrollIndicator from "./ScrollIndicator";

export default function Hero(): React.JSX.Element {
  return (
    <section className="relative overflow-hidden bg-slate-950 py-28">
      {/* Animated Background */}
      <AnimatedBackground />

      <Container>
        <div className="relative z-10 mx-auto max-w-4xl text-center">

          {/* Welcome Text */}
          <motion.p
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            className="mb-6 text-lg font-semibold uppercase tracking-[0.3em] text-cyan-400"
          >
            Welcome to OceanAI
          </motion.p>

          {/* Heading */}
          <motion.h1
            initial={{ opacity: 0, y: 60 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              delay: 0.2,
              duration: 0.8,
            }}
            className="text-5xl font-extrabold leading-tight text-white md:text-7xl"
          >
            AI-Powered
            <br />
            Ocean Intelligence
          </motion.h1>

          {/* Description */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{
              delay: 0.6,
            }}
            className="mx-auto mt-8 max-w-2xl text-lg leading-8 text-slate-300"
          >
            Monitor, analyze and protect marine ecosystems using Artificial
            Intelligence, Machine Learning, and real-time ocean data.
          </motion.p>

          {/* Buttons */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{
              delay: 1,
            }}
            className="mt-10 flex flex-col justify-center gap-4 sm:flex-row"
          >
            <OceanButton variant="primary">
              Get Started
            </OceanButton>

            <OceanButton variant="outline">
              🌍 Try Live Demo
            </OceanButton>
          </motion.div>

          {/* Statistics */}
          <HeroStats />

        </div>
      </Container>

      {/* Scroll Indicator */}
      <ScrollIndicator />
    </section>
  );
}