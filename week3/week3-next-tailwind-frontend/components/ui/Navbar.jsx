'use client';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Input from "./Input";

export default function Navbar() {
  const pathname = usePathname();
  const isLandingPage = pathname === "/";

  return (
    <header className={`h-16 flex items-center justify-between px-6 sticky top-0 z-50 transition-colors duration-300 ${
      isLandingPage 
        ? "bg-[#1e0b36] border-b border-white/10" 
        : "bg-slate-900 border-b border-slate-800"
    }`}>
      
      <div className="flex items-center gap-4">
        <button className="text-xl text-slate-300 hover:text-white transition">☰</button>
        <Link href="/">
          <span className="text-white font-bold text-lg tracking-tight">Hestabit</span>
        </Link>
      </div>

      <div className="flex items-center gap-6">
        {isLandingPage ? (
          <Link href="/about" className="text-slate-300 text-[18px] hover:text-white text-sm font-medium transition">
            About
          </Link>
        ) : (
          <div className="hidden sm:flex items-center rounded-md border border-slate-700 bg-slate-800">
            <Input placeholder="Search..." className="bg-transparent border-none text-slate-200 px-3 py-1 w-full" />
            <button className="px-3 py-2 bg-white text-slate-900">🔍</button>
          </div>
        )}

        <Link href="/dashboard/profile">
          <div className="w-9 h-9 flex items-center justify-center rounded-full bg-white text-slate-900 hover:bg-slate-100 transition">
            👤
          </div>
        </Link>
      </div>
    </header>
  );
}