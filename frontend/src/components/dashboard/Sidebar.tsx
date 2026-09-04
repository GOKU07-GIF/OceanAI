import {
  LayoutDashboard,
  Database,
  Map,
  BrainCircuit,
  Bot,
  Bell,
  FileText,
  Settings,
  LogOut,
} from "lucide-react";

import { NavLink, useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";

interface MenuItem {
  title: string;
  path: string;
  icon: React.ElementType;
}

const menuItems: MenuItem[] = [
  {
    title: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Ocean Data",
    path: "/dashboard/ocean-data",
    icon: Database,
  },
  {
    title: "Ocean Map",
    path: "/dashboard/map",
    icon: Map,
  },
  {
    title: "AI Analytics",
    path: "/dashboard/analytics",
    icon: BrainCircuit,
  },
  {
    title: "ORCA Assistant",
    path: "/dashboard/orca",
    icon: Bot,
  },
  {
    title: "Alerts",
    path: "/dashboard/alerts",
    icon: Bell,
  },
  {
    title: "Reports",
    path: "/dashboard/reports",
    icon: FileText,
  },
  {
    title: "Settings",
    path: "/dashboard/settings",
    icon: Settings,
  },
];

export default function Sidebar(): React.JSX.Element {
  const navigate = useNavigate();
  const { logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

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
      <div className="border-b border-slate-200 p-6 dark:border-slate-800">
        <h1 className="text-3xl font-bold text-cyan-500 dark:text-cyan-400">
          🌊 OceanAI
        </h1>

        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Ocean Intelligence Platform
        </p>
      </div>

      {/* Menu */}
      <nav className="flex-1 space-y-2 p-4">
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.title}
              to={item.path}
              end={item.path === "/dashboard"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-4 py-3 transition-colors ${
                  isActive
                    ? "bg-cyan-600 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
                }`
              }
            >
              <Icon size={20} />

              <span>{item.title}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-slate-200 p-4 dark:border-slate-800">
        <button
          type="button"
          onClick={handleLogout}
          className="
            flex w-full items-center gap-3 rounded-xl px-4 py-3
            text-red-500 transition hover:bg-red-500/10
            dark:text-red-400
          "
        >
          <LogOut size={20} />

          Logout
        </button>
      </div>
    </aside>
  );
}
