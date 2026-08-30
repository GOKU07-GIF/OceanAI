import {
  TrendingUp,
  Waves,
  Thermometer,
  Activity,
} from "lucide-react";

export default function Analytics(): React.JSX.Element {
  return (
    <div className="space-y-6">

      {/* PAGE HEADER */}
      <div>
        <h1 className="text-3xl font-bold text-white">
          Ocean Analytics
        </h1>

        <p className="mt-1 text-slate-400">
          Analyze ocean conditions and environmental trends.
        </p>
      </div>

      {/* ANALYTICS CARDS */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">

        {/* TEMPERATURE */}
        <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
          <div className="flex items-center justify-between">

            <div>
              <p className="text-sm text-slate-400">
                Average Temperature
              </p>

              <h2 className="mt-2 text-3xl font-bold text-orange-400">
                28.5°C
              </h2>
            </div>

            <div className="rounded-xl bg-slate-700 p-3">
              <Thermometer
                size={28}
                className="text-orange-400"
              />
            </div>

          </div>
        </div>

        {/* WAVE HEIGHT */}
        <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
          <div className="flex items-center justify-between">

            <div>
              <p className="text-sm text-slate-400">
                Wave Height
              </p>

              <h2 className="mt-2 text-3xl font-bold text-cyan-400">
                2.4 m
              </h2>
            </div>

            <div className="rounded-xl bg-slate-700 p-3">
              <Waves
                size={28}
                className="text-cyan-400"
              />
            </div>

          </div>
        </div>

        {/* WATER QUALITY */}
        <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
          <div className="flex items-center justify-between">

            <div>
              <p className="text-sm text-slate-400">
                Water Quality
              </p>

              <h2 className="mt-2 text-3xl font-bold text-green-400">
                Excellent
              </h2>
            </div>

            <div className="rounded-xl bg-slate-700 p-3">
              <Activity
                size={28}
                className="text-green-400"
              />
            </div>

          </div>
        </div>

        {/* TREND */}
        <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
          <div className="flex items-center justify-between">

            <div>
              <p className="text-sm text-slate-400">
                Weekly Trend
              </p>

              <h2 className="mt-2 text-3xl font-bold text-purple-400">
                +12.4%
              </h2>
            </div>

            <div className="rounded-xl bg-slate-700 p-3">
              <TrendingUp
                size={28}
                className="text-purple-400"
              />
            </div>

          </div>
        </div>

      </div>

      {/* INSIGHTS */}
      <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">

        <h2 className="text-xl font-semibold text-white">
          AI Ocean Insights
        </h2>

        <div className="mt-5 space-y-4">

          <div className="rounded-xl border border-cyan-900 bg-slate-900 p-4">
            <p className="font-medium text-cyan-400">
              🌊 Stable Ocean Conditions
            </p>

            <p className="mt-2 text-sm text-slate-400">
              Current ocean conditions are stable with normal temperature
              and wave activity.
            </p>
          </div>

          <div className="rounded-xl border border-green-900 bg-slate-900 p-4">
            <p className="font-medium text-green-400">
              ✓ Water Quality is Healthy
            </p>

            <p className="mt-2 text-sm text-slate-400">
              The latest sensor readings indicate healthy water quality
              conditions.
            </p>
          </div>

          <div className="rounded-xl border border-orange-900 bg-slate-900 p-4">
            <p className="font-medium text-orange-400">
              ⚠ Monitor Temperature
            </p>

            <p className="mt-2 text-sm text-slate-400">
              Temperature is slightly above the normal baseline and should
              continue to be monitored.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}