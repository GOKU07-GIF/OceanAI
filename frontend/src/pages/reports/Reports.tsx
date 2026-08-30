import {
  FileText,
  Download,
  Eye,
  Database,
  Thermometer,
  Droplets,
  BrainCircuit,
} from "lucide-react";

interface Report {
  id: number;
  title: string;
  description: string;
  date: string;
  icon: React.ElementType;
  color: string;
}

const reports: Report[] = [
  {
    id: 1,
    title: "Ocean Data Report",
    description: "Complete summary of collected ocean monitoring data.",
    date: "Today",
    icon: Database,
    color: "text-cyan-400",
  },
  {
    id: 2,
    title: "Temperature Analysis Report",
    description: "Analysis of recent ocean temperature readings.",
    date: "Today",
    icon: Thermometer,
    color: "text-orange-400",
  },
  {
    id: 3,
    title: "Water Quality Report",
    description: "Water quality analysis including pH and sensor readings.",
    date: "Yesterday",
    icon: Droplets,
    color: "text-purple-400",
  },
  {
    id: 4,
    title: "AI Ocean Analysis Report",
    description: "AI-generated insights and environmental predictions.",
    date: "Yesterday",
    icon: BrainCircuit,
    color: "text-green-400",
  },
];

export default function Reports(): React.JSX.Element {
  return (
    <div className="min-h-full p-6">

      {/* Page Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">
            Reports
          </h1>

          <p className="mt-2 text-slate-400">
            View and download ocean monitoring reports.
          </p>
        </div>

        <button className="flex items-center gap-2 rounded-xl bg-cyan-600 px-5 py-3 font-medium text-white transition hover:bg-cyan-500">
          <FileText size={20} />
          Generate Report
        </button>
      </div>

      {/* Statistics */}
      <div className="mb-8 grid gap-6 md:grid-cols-3">

        <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
          <p className="text-slate-400">
            Total Reports
          </p>

          <h2 className="mt-2 text-3xl font-bold text-cyan-400">
            12
          </h2>
        </div>

        <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
          <p className="text-slate-400">
            Generated Today
          </p>

          <h2 className="mt-2 text-3xl font-bold text-green-400">
            3
          </h2>
        </div>

        <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">
          <p className="text-slate-400">
            AI Reports
          </p>

          <h2 className="mt-2 text-3xl font-bold text-purple-400">
            5
          </h2>
        </div>

      </div>

      {/* Reports List */}
      <div className="rounded-2xl border border-slate-700 bg-slate-800 p-6">

        <h2 className="mb-6 text-xl font-semibold text-white">
          Recent Reports
        </h2>

        <div className="space-y-4">

          {reports.map((report) => {
            const Icon = report.icon;

            return (
              <div
                key={report.id}
                className="flex flex-col gap-4 rounded-xl border border-slate-700 bg-slate-900 p-5 transition hover:border-cyan-500 md:flex-row md:items-center md:justify-between"
              >
                <div className="flex items-start gap-4">

                  <div className="rounded-xl bg-slate-800 p-3">
                    <Icon
                      size={26}
                      className={report.color}
                    />
                  </div>

                  <div>
                    <h3 className="font-semibold text-white">
                      {report.title}
                    </h3>

                    <p className="mt-1 text-sm text-slate-400">
                      {report.description}
                    </p>

                    <p className="mt-2 text-sm text-slate-500">
                      Generated: {report.date}
                    </p>
                  </div>

                </div>

                <div className="flex gap-3">

                  <button className="flex items-center gap-2 rounded-lg bg-slate-700 px-4 py-2 text-sm text-white transition hover:bg-slate-600">
                    <Eye size={17} />
                    View
                  </button>

                  <button className="flex items-center gap-2 rounded-lg bg-cyan-600 px-4 py-2 text-sm text-white transition hover:bg-cyan-500">
                    <Download size={17} />
                    Download
                  </button>

                </div>

              </div>
            );
          })}

        </div>

      </div>

    </div>
  );
}