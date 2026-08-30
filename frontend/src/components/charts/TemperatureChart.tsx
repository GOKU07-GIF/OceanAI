import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

interface TemperatureData {
  day: string;
  temperature: number;
}

const data: TemperatureData[] = [
  { day: "Mon", temperature: 27 },
  { day: "Tue", temperature: 29 },
  { day: "Wed", temperature: 28 },
  { day: "Thu", temperature: 31 },
  { day: "Fri", temperature: 30 },
  { day: "Sat", temperature: 29 },
  { day: "Sun", temperature: 28 },
];

export default function TemperatureChart(): React.JSX.Element {
  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6 shadow-lg">
      <h2 className="mb-6 text-xl font-bold text-white">
        Temperature Trend
      </h2>

      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#334155"
          />

          <XAxis
            dataKey="day"
            stroke="#94a3b8"
          />

          <YAxis stroke="#94a3b8" />

          <Tooltip />

          <Line
            type="monotone"
            dataKey="temperature"
            stroke="#06b6d4"
            strokeWidth={3}
            dot={{ r: 4 }}
            activeDot={{ r: 7 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}