import {
  LayoutDashboard,
  Database,
  Map,
  ChartColumn,
  Bell,
  FileText,
  Settings,
  LogOut,
} from "lucide-react";

import { NavLink } from "react-router-dom";

interface MenuItem {
  name: string;
  icon: React.ElementType;
  path: string;
}

const menu: MenuItem[] = [
  {
    name: "Dashboard",
    icon: LayoutDashboard,
    path: "/dashboard",
  },
  {
    name: "Ocean Data",
    icon: Database,
    path: "/dashboard/ocean-data",
  },
  {
    name: "Ocean Map",
    icon: Map,
    path: "/dashboard/map",
  },
  {
    name: "AI Analytics",
    icon: ChartColumn,
    path: "/dashboard/analytics",
  },
  {
    name: "Alerts",
    icon: Bell,
    path: "/dashboard/alerts",
  },
  {
    name: "Reports",
    icon: FileText,
    path: "/dashboard/reports",
  },
  {
    name: "Settings",
    icon: Settings,
    path: "/dashboard/settings",
  },
];

export default function Sidebar(): React.JSX.Element {
  return (
    <aside
      className="
        flex h-screen w-72 flex-col
        border-r border-slate-200 bg-white text-slate-900
        transition-colors duration-300
        dark:border-slate-800 dark:bg-slate-900 dark:text-white
      "
    >
      {/* Logo */}
      <div
        className="
          border-b border-slate-200 px-6 py-7
          dark:border-slate-800
        "
      >
        <h1 className="text-3xl font-bold text-cyan-500 dark:text-cyan-400">
          🌊 OceanAI
        </h1>

        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Ocean Intelligence Platform
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 px-4 py-5">
        {menu.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.name}
              to={item.path}
              end={item.path === "/dashboard"}
              className={({ isActive }) =>
                `
                  flex w-full items-center gap-4 rounded-xl px-5 py-3
                  transition-colors duration-200
                  ${
                    isActive
                      ? "bg-cyan-600 text-white"
                      : `
                        text-slate-600 hover:bg-slate-100 hover:text-slate-900
                        dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white
                      `
                  }
                `
              }
            >
              <Icon size={21} />

              <span className="font-medium">
                {item.name}
              </span>
            </NavLink>
          );
        })}
      </nav>

      {/* Logout */}
      <div
        className="
          border-t border-slate-200 p-4
          dark:border-slate-800
        "
      >
        <NavLink
          to="/login"
          className="
            flex items-center gap-4 rounded-xl px-5 py-3
            text-red-500 transition hover:bg-red-500/10
            dark:text-red-400
          "
        >
          <LogOut size={21} />

          <span className="font-medium">
            Logout
          </span>
        </NavLink>
      </div>
    </aside>
  );
}