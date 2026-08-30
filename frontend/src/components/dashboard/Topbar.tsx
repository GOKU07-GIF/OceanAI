import {
  Bell,
  Search,
  UserCircle,
} from "lucide-react";

export default function Topbar(): React.JSX.Element {
  return (
    <header className="flex h-20 items-center justify-between border-b border-slate-800 bg-slate-900 px-8">

      {/* Left */}
      <div>
        <h1 className="text-2xl font-bold text-white">
          Dashboard
        </h1>

        <p className="text-sm text-slate-400">
          Welcome to OceanAI
        </p>
      </div>

      {/* Right */}
      <div className="flex items-center gap-4">

        <div className="relative">
          <Search
            size={18}
            className="absolute left-3 top-3 text-slate-400"
          />

          <input
            type="text"
            placeholder="Search..."
            className="w-72 rounded-xl border border-slate-700 bg-slate-800 py-2 pl-10 pr-4 text-white outline-none focus:border-cyan-500"
          />
        </div>

        <button className="rounded-xl bg-slate-800 p-3 transition hover:bg-slate-700">
          <Bell
            size={20}
            className="text-white"
          />
        </button>

        <button className="rounded-full bg-slate-800 p-2 transition hover:bg-slate-700">
          <UserCircle
            size={34}
            className="text-cyan-400"
          />
        </button>

      </div>

    </header>
  );
}