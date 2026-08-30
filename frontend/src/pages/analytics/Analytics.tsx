import { Activity, Thermometer, Waves, Database } from "lucide-react";

import { useDashboard } from "../../hooks/useDashboard";

export default function Analytics(): React.JSX.Element {
  const { data, isLoading, isError, error } = useDashboard();

  if (isLoading) {
    return (
      <div className="p-6 text-slate-300">
        Loading analytics...
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="rounded-2xl border border-red-500/30 bg-red-500/5 p-6 text-red-400">
        <h1 className="text-xl font-semibold">Unable to load analytics</h1>
        <p className="mt-2 text-sm text-slate-400">
          {error instanceof Error ? error.message : "Please try again later."}
        </p>
      </div>
    );
  }

  const waterQualityLabel =
    data.water_quality >= 80
      ? "Excellent"
      : data.water_quality >= 60
        ? "Moderate"
        : "Needs Attention";

  const riskLabel = data.ai_risk;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Ocean Analytics</h1>
        <p className="mt-1 text-slate-400">
          Live analytics calculated from the OceanAI database.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Average Temperature"
          value={`${data.average_temperature}°C`}
          icon={<Thermometer size={28} className="text-orange-400" />}
        />

        <MetricCard
          title="Average Salinity"
          value={data.salinity.toString()}
          icon={<Waves size={28} className="text-cyan-400" />}
        />

        <MetricCard
          title="Water Quality"
          value={waterQualityLabel}
          icon={<Activity size={28} className="text-green-400" />}
        />

        <MetricCard
          title="AI Risk"
          value={riskLabel}
          icon={<Database size={28} className="text-purple-400" />}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <InfoCard label="Average pH" value={data.average_ph.toString()} />
        <InfoCard label="Average Oxygen" value={data.oxygen.toString()} />
        <InfoCard label="Ocean Records" value={data.total_records.toString()} />
      </div>

      <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
        <h2 className="text-xl font-semibold text-white">Current Ocean Insight</h2>
        <p className="mt-3 text-slate-300">
          The current dashboard risk level is <strong>{riskLabel}</strong>.
          Water quality is classified as <strong>{waterQualityLabel}</strong>
          based on the metrics currently stored in OceanData.
        </p>
        <p className="mt-3 text-sm text-slate-500">
          This page intentionally does not display wave height or weekly percentage
          values because the current OceanData model does not provide those measurements.
        </p>
      </div>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
}

function MetricCard({ title, value, icon }: MetricCardProps): React.JSX.Element {
  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">{title}</p>
          <h2 className="mt-2 text-3xl font-bold text-white">{value}</h2>
        </div>
        <div className="rounded-xl bg-slate-700 p-3">{icon}</div>
      </div>
    </div>
  );
}

interface InfoCardProps {
  label: string;
  value: string;
}

function InfoCard({ label, value }: InfoCardProps): React.JSX.Element {
  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-800 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-bold text-white">{value}</p>
    </div>
  );
}
