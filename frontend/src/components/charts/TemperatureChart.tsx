import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

import { useOceanData } from "../../hooks/useOceanData";

interface TemperatureData {
  label: string;
  temperature: number;
}

export default function TemperatureChart(): React.JSX.Element {
  const { data: oceanData = [], isLoading, isError } = useOceanData();

  const data: TemperatureData[] = oceanData
    .slice()
    .sort(
      (a, b) =>
        new Date(a.created_at).getTime() -
        new Date(b.created_at).getTime(),
    )
    .slice(-12)
    .map((record) => ({
      label: new Date(record.created_at).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      temperature: record.temperature,
    }));

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6 shadow-lg">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Temperature Trend</h2>
        <span className="text-xs text-slate-500">Latest OceanData records</span>
      </div>

      {isLoading && (
        <div className="flex h-[320px] items-center justify-center text-slate-400">
          Loading temperature data...
        </div>
      )}

      {isError && (
        <div className="flex h-[320px] items-center justify-center text-red-400">
          Unable to load temperature data.
        </div>
      )}

      {!isLoading && !isError && data.length === 0 && (
        <div className="flex h-[320px] items-center justify-center text-slate-400">
          No ocean temperature records available.
        </div>
      )}

      {!isLoading && !isError && data.length > 0 && (
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="label" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="temperature"
              name="Temperature (°C)"
              stroke="#06b6d4"
              strokeWidth={3}
              dot={{ r: 4 }}
              activeDot={{ r: 7 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
