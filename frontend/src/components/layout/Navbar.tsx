import {
  Bell,
  Search,
  UserCircle,
} from "lucide-react";

export default function Navbar(): React.JSX.Element {
  return (
    <header
      className="
        flex items-center justify-between
        border-b border-slate-200 bg-white
        px-8 py-5
        transition-colors duration-300
        dark:border-slate-800 dark:bg-slate-950
      "
    >
      {/* Search */}
      <div
        className="
          flex w-96 items-center gap-3 rounded-xl
          bg-slate-100 px-4 py-2
          transition-colors duration-300
          dark:bg-slate-900
        "
      >
        <Search
          size={18}
          className="text-slate-500 dark:text-slate-400"
        />

        <input
          type="text"
          placeholder="Search..."
          className="
            w-full bg-transparent
            text-slate-900 outline-none
            placeholder:text-slate-500
            dark:text-white
          "
        />
      </div>

      {/* Right Icons */}
      <div
        className="
          flex items-center gap-6
          text-slate-700
          dark:text-white
        "
      >
        <Bell
          size={22}
          className="
            cursor-pointer transition
            hover:text-cyan-500
            dark:hover:text-cyan-400
          "
        />

        <UserCircle
          size={38}
          className="
            cursor-pointer transition
            hover:text-cyan-500
            dark:hover:text-cyan-400
          "
        />
      </div>
    </header>
  );
}