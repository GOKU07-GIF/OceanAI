import { useDashboard } from "../../hooks/useDashboard";
import StatCard from "../../components/dashboard/StatCard";
import TemperatureChart from "../../components/charts/TemperatureChart";

export default function Dashboard(): React.JSX.Element {
  const { data, isLoading, isError } = useDashboard();

  if (isLoading) {
    return (
      <div className="p-10 text-slate-900 dark:text-white">
        Loading Dashboard...
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-10 text-red-500">
        Failed to load dashboard.
      </div>
    );
  }

  return (
    <div className="space-y-8 p-8">
      <div>
        <h1 className="text-4xl font-bold text-slate-900 dark:text-white">
          OceanAI Dashboard
        </h1>

        <p className="mt-2 text-slate-500 dark:text-slate-400">
          Real-time ocean monitoring system
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Total Records"
          value={data.total_records}
          icon="records"
        />

        <StatCard
          title="Users"
          value={data.total_users}
          color="text-green-500 dark:text-green-400"
          icon="users"
        />

        <StatCard
          title="Temperature"
          value={data.average_temperature}
          unit="°C"
          color="text-orange-500 dark:text-orange-400"
          icon="temperature"
        />

        <StatCard
          title="Average pH"
          value={data.average_ph}
          color="text-purple-500 dark:text-purple-400"
          icon="ph"
        />
      </div>

      <TemperatureChart />
    </div>
  );
}