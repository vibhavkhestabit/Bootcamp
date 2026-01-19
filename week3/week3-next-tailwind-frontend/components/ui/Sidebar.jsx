export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col shadow-lg">
      {/* Brand */}
      <div className="h-16 flex items-center px-6 text-lg font-semibold tracking-wide border-b border-slate-800">
        <span className="text-indigo-400">●</span>
        <span className="ml-2">Start Bootstrap</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-6 text-sm">
        {/* Core */}
        <p className="px-3 mb-2 text-xs font-semibold uppercase text-slate-500">
          Core
        </p>

        <a className="flex items-center gap-3 px-3 py-2 mb-1 rounded-md bg-slate-800 text-white shadow-inner">
          <span>📊</span>
          Dashboard
        </a>

        {/* Interface */}
        <p className="px-3 mt-6 mb-2 text-xs font-semibold uppercase text-slate-500">
          Interface
        </p>

        {["Layouts", "Pages"].map((item) => (
          <a
            key={item}
            className="flex items-center gap-3 px-3 py-2 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition-colors duration-200"
          >
            ▸ {item}
          </a>
        ))}

        {/* Addons */}
        <p className="px-3 mt-6 mb-2 text-xs font-semibold uppercase text-slate-500">
          Addons
        </p>

        {["Charts", "Tables"].map((item) => (
          <a
            key={item}
            className="flex items-center gap-3 px-3 py-2 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition-colors duration-200"
          >
            ▸ {item}
          </a>
        ))}
      </nav>
    </aside>
  );
}
