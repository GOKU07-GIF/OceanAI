import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  Compass,
  MapPin,
  MessageCircle,
  Send,
  Thermometer,
  Waves,
  Wind,
} from "lucide-react";

interface ConditionCardProps {
  label: string;
  value: string;
  unit?: string;
  icon: React.ReactNode;
}

function ConditionCard({
  label,
  value,
  unit,
  icon,
}: ConditionCardProps): React.JSX.Element {
  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-800 p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">{label}</p>
          <p className="mt-2 text-2xl font-bold text-white">
            {value}
            {unit && <span className="ml-1 text-sm font-normal text-slate-400">{unit}</span>}
          </p>
        </div>
        <div className="rounded-xl bg-slate-700 p-3 text-cyan-400">{icon}</div>
      </div>
    </div>
  );
}

export default function Orca(): React.JSX.Element {
  return (
    <div className="space-y-6">
      {/* HEADER */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-cyan-500/10 p-3 text-cyan-400">
              <Bot size={30} />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">ORCA Assistant</h1>
              <p className="mt-1 text-sm text-slate-400">
                Ocean Research & Catch Advisory
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start rounded-full border border-green-500/20 bg-green-500/10 px-4 py-2 text-sm font-medium text-green-400 md:self-auto">
          <span className="h-2 w-2 rounded-full bg-green-400" />
          Ready
        </div>
      </div>

      {/* ASK ORCA */}
      <section className="rounded-2xl border border-cyan-500/20 bg-slate-800 p-6 shadow-lg shadow-cyan-950/10">
        <div className="flex items-center gap-2 text-white">
          <MessageCircle size={20} className="text-cyan-400" />
          <h2 className="text-xl font-semibold">Ask ORCA</h2>
        </div>
        <p className="mt-2 text-sm text-slate-400">
          Ask about ocean conditions, fishing suitability, safety, or marine observations.
        </p>

        <div className="mt-5 flex flex-col gap-3 md:flex-row">
          <input
            type="text"
            placeholder="e.g. Is it safe to go fishing near Mumbai tomorrow?"
            className="min-w-0 flex-1 rounded-xl border border-slate-600 bg-slate-900 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-cyan-400"
          />
          <button
            type="button"
            className="flex items-center justify-center gap-2 rounded-xl bg-cyan-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400"
          >
            <Send size={18} />
            Ask ORCA
          </button>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {[
            "Fishing conditions near Mumbai",
            "Ocean safety tomorrow",
            "Best conditions for fishing",
          ].map((question) => (
            <button
              key={question}
              type="button"
              className="rounded-full border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-slate-300 transition hover:border-cyan-500/50 hover:text-cyan-300"
            >
              {question}
            </button>
          ))}
        </div>
      </section>

      {/* CURRENT ORCA RESPONSE */}
      <section className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-cyan-500/10 p-2 text-cyan-400">
            <Bot size={22} />
          </div>
          <div>
            <h2 className="font-semibold text-white">ORCA Recommendation</h2>
            <p className="text-xs text-slate-500">Waiting for your question</p>
          </div>
        </div>

        <div className="mt-5 rounded-xl border border-dashed border-slate-700 bg-slate-900/60 p-6 text-center">
          <Compass size={32} className="mx-auto text-slate-600" />
          <p className="mt-3 text-slate-400">
            Ask ORCA a question to generate an ocean intelligence recommendation.
          </p>
          <p className="mt-1 text-xs text-slate-600">
            Live environmental evidence will appear here after backend integration.
          </p>
        </div>
      </section>

      {/* ENVIRONMENT SNAPSHOT */}
      <section>
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-white">Environment Snapshot</h2>
          <p className="mt-1 text-sm text-slate-400">
            These fields will be populated from real marine and weather providers.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <ConditionCard
            label="Sea Temperature"
            value="—"
            unit="°C"
            icon={<Thermometer size={22} />}
          />
          <ConditionCard
            label="Wave Height"
            value="—"
            unit="m"
            icon={<Waves size={22} />}
          />
          <ConditionCard
            label="Wind Speed"
            value="—"
            unit="m/s"
            icon={<Wind size={22} />}
          />
          <ConditionCard
            label="Location"
            value="—"
            icon={<MapPin size={22} />}
          />
        </div>
      </section>

      {/* DECISION PANEL */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-green-500/20 bg-green-950/10 p-6">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="text-green-400" size={24} />
            <h2 className="text-xl font-semibold text-white">Fishing Suitability</h2>
          </div>
          <p className="mt-4 text-slate-400">
            ORCA will combine environmental indicators to estimate whether conditions are
            favorable for fishing.
          </p>
          <div className="mt-5 rounded-xl bg-slate-900/70 p-4 text-sm text-slate-500">
            Recommendation will appear after ORCA receives real ocean evidence.
          </div>
        </section>

        <section className="rounded-2xl border border-amber-500/20 bg-amber-950/10 p-6">
          <div className="flex items-center gap-3">
            <AlertTriangle className="text-amber-400" size={24} />
            <h2 className="text-xl font-semibold text-white">Risk Factors</h2>
          </div>
          <ul className="mt-4 space-y-3 text-sm text-slate-400">
            <li className="rounded-lg bg-slate-900/60 p-3">No live risk assessment yet.</li>
            <li className="rounded-lg bg-slate-900/60 p-3">Weather and wave conditions will be evaluated.</li>
            <li className="rounded-lg bg-slate-900/60 p-3">Ocean indicators will support the final recommendation.</li>
          </ul>
        </section>
      </div>
    </div>
  );
}
