export default function Navbar() {
  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shadow-sm">
      {/* Left */}
      <div className="flex items-center gap-4">
        <button className="text-xl text-gray-600 hover:text-black transition">
          ☰
        </button>
        <span className="text-sm text-gray-500 hidden md:block">
          Dashboard
        </span>
      </div>

      {/* Right */}
      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="hidden sm:flex items-center overflow-hidden rounded-md border border-gray-300 focus-within:ring-2 focus-within:ring-indigo-500">
          <input
            placeholder="Search..."
            className="px-3 py-1.5 text-sm outline-none"
          />
          <button className="bg-indigo-600 px-3 py-2 text-white hover:bg-indigo-700 transition">
            🔍
          </button>
        </div>

        {/* Avatar */}
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 shadow-md" />
      </div>
    </header>
  );
}
