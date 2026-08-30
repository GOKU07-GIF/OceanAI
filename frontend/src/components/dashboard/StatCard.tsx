import {
  Database,
  Users,
  Thermometer,
  Droplets,
  LucideIcon,
} from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  unit?: string;
  color?: string;
  icon?: "records" | "users" | "temperature" | "ph";
}

const icons: Record<
  NonNullable<StatCardProps["icon"]>,
  LucideIcon
> = {
  records: Database,
  users: Users,
  temperature: Thermometer,
  ph: Droplets,
};

export default function StatCard({
  title,
  value,
  unit = "",
  color = "text-cyan-500 dark:text-cyan-400",
  icon = "records",
}: StatCardProps): React.JSX.Element {
  const Icon = icons[icon];

  return (
    <div
      className="
        rounded-2xl border
        border-slate-200 bg-white
        p-6 shadow-lg
        transition-all duration-300
        hover:border-cyan-500 hover:shadow-cyan-500/20

        dark:border-slate-700 dark:bg-slate-800
      "
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {title}
          </p>

          <h2 className={`mt-3 text-3xl font-bold ${color}`}>
            {value}

            {unit && (
              <span className="ml-2 text-lg text-slate-500 dark:text-slate-400">
                {unit}
              </span>
            )}
          </h2>
        </div>

        <div
          className="
            rounded-xl bg-slate-100 p-3
            dark:bg-slate-700
          "
        >
          <Icon className={`h-7 w-7 ${color}`} />
        </div>
      </div>
    </div>
  );
}