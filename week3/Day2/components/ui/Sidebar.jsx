import Link from "next/link";

export default function Sidebar() {
  return (
    <aside className="w-72 bg-gradient-to-b from-slate-900 to-blue-900 text-slate-200 flex flex-col shadow-lg border-r border-blue-800 h-screen sticky top-0">
      <nav className="flex-1 px-4 py-8 text-base">
        <p className="px-4 mb-3 text-sm font-bold uppercase text-slate-400 tracking-widest">
          Core
        </p>

        <Link 
          href="/dashboard" 
          className="flex items-center gap-4 px-4 py-3 mb-2 rounded-md bg-white/10 text-white shadow-md cursor-pointer hover:bg-white/20 transition-all decoration-0"
        >
          <span className="font-semibold">Dashboard</span>
        </Link>

        <p className="px-4 mt-8 mb-3 text-sm font-bold uppercase text-slate-400 tracking-widest">
          Interface
        </p>

        <Link
          href="/dashboard/users"
          className="flex items-center justify-between px-4 py-3 rounded-md text-slate-300 hover:bg-white/10 hover:text-white transition-all cursor-pointer mb-1 decoration-0"
        >
          <div className="flex items-center gap-4">
            <span className="font-medium text-lg">Users</span>
          </div>
        </Link>


        <a className="flex items-center justify-between px-4 py-3 rounded-md text-slate-300 hover:bg-white/10 hover:text-white transition-all cursor-pointer mb-1">
          <div className="flex items-center gap-4">
            <span className="font-medium text-lg">Pages</span>
          </div>
        </a>

        <p className="px-4 mt-8 mb-3 text-sm font-bold uppercase text-slate-400 tracking-widest">
          Addons
        </p>

        {["Charts", "Tables"].map((item) => (
          <a
            key={item}
            className="flex items-center gap-4 px-4 py-3 rounded-md text-slate-300 hover:bg-white/10 hover:text-white transition-all cursor-pointer mb-1"
          >
            <span className="font-medium text-lg">{item}</span>
          </a>
        ))}
      </nav>
    </aside>
  );
}