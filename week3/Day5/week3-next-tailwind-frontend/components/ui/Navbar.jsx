'use client';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Input from "./Input";
import Button from "@/components/ui/Button";

export default function Navbar() {
  const pathname = usePathname();
  const isLandingPage = pathname === "/";
  const isLoginPage = pathname === "/login";
  const isDashboard = pathname.startsWith("/dashboard");

  if (isLoginPage) return null;

  return (
    <header className={`h-16 flex items-center justify-between px-6 sticky top-0 z-50 transition-colors duration-300 ${
      isLandingPage 
        ? "bg-[#1e0b36] border-b border-white/10" 
        : "bg-slate-900 border-b border-slate-800"
    }`}>
      
      {/* LEFT: Branding */}
      <div className="flex items-center gap-4">
        <button className="text-slate-300 hover:text-white transition">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <Link href="/">
          <span className="text-white font-bold text-lg tracking-tight uppercase">Hestabit</span>
        </Link>
      </div>

      {/* RIGHT: Combined Actions Grid */}
      <div className="flex items-center gap-6">
        
        {isLandingPage && (
          <Link href="/about" className="text-slate-300 hover:text-white text-sm font-medium transition">
            About
          </Link>
        )}

        {isDashboard && (
          <div className="hidden sm:flex items-center rounded-md border border-slate-700 bg-slate-800 overflow-hidden">
            <Input placeholder="Search..." className="bg-transparent border-none text-slate-200 px-3 py-1 w-full outline-none" />
            <button className="px-3 py-2 bg-white text-slate-900 hover:bg-slate-100 transition">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </div>
        )}

        {!isDashboard && (
          <Link href="/login">
            <Button className={`rounded-full px-8 py-2 text-xs font-black uppercase tracking-widest transition-all duration-300 ${
              isLoginPage 
                ? "!bg-green-600 hover:!bg-green-700 !shadow-[0_0_20px_rgba(22,163,74,0.4)]" 
                : "!bg-red-500 hover:!bg-red-600 !shadow-[0_0_20px_rgba(239,68,68,0.4)]"
            }`}>
              Login
            </Button>
          </Link>
        )}
        
        {isDashboard && (
          <Link href="/dashboard/profile">
            <div className="w-9 h-9 flex items-center justify-center rounded-full bg-white text-slate-900 hover:bg-slate-100 transition shadow-sm">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </Link>
        )}
      </div>
    </header>
  );
}