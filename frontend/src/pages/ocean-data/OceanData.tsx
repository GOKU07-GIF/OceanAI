import { Database } from "lucide-react";

export default function OceanData(): React.JSX.Element {
  return (
    <div className="min-h-full p-6 text-white">

      <div className="mb-8">
        <h1 className="text-4xl font-bold">
          Ocean Data
        </h1>

        <p className="mt-2 text-slate-400">
          View and manage real-time ocean monitoring data.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-700 bg-slate-800 p-8">
        <div className="flex items-center gap-4">
          <div className="rounded-xl bg-cyan-500/10 p-4 text-cyan-400">
            <Database size={32} />
          </div>

          <div>
            <h2 className="text-xl font-semibold">
              Ocean Monitoring Data
            </h2>

            <p className="mt-1 text-slate-400">
              Ocean sensor and environmental data will appear here.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
}