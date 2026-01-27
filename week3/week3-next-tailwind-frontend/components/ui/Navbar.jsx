import Input from "./Input";

export default function Navbar() {
  return (
    <header className="h-16 bg-gradient-to-r from-slate-900 to-blue-900 border-b border-blue-800 flex items-center justify-between px-6 shadow-sm">
      
      <div className="flex items-center gap-4">
        <button
          className="text-xl text-slate-300 hover:text-white transition"
          aria-label="Toggle Sidebar"
        >
          ☰
        </button>

        <span className="text-white font-bold text-lg tracking-tight">
          Start Bootstrap
        </span>
      </div>

      <div className="flex items-center gap-4">
      
        <div className="hidden sm:flex items-center overflow-hidden rounded-md border border-slate-700 bg-slate-800 focus-within:ring-2 focus-within:ring-blue-500">
          
          <Input
            placeholder="Search..."
            className="bg-transparent border-none text-slate-200 placeholder-slate-400 px-3 py-1.5 w-full focus:ring-0"
          />
          
          <button className="px-3 py-2 bg-white text-slate-900 hover:bg-slate-100 transition border-l border-slate-700">
            🔍
          </button>
        </div>

        <div className="w-9 h-9 flex items-center justify-center rounded-full bg-white border border-slate-300 text-slate-900 hover:bg-slate-100 cursor-pointer transition">
          👤
        </div>
      </div>
    </header>
  );
}