import Image from "next/image";
import Link from "next/link";
import Button from "@/components/ui/Button";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#0f0720] overflow-hidden selection:bg-orange-500">
      
      <section className="w-full bg-gradient-to-br from-[#1e0b36] via-[#2e1065] to-[#0f0720] pt-24 pb-48 rounded-bl-[100px] md:rounded-bl-[200px] relative">
        <div className="absolute top-0 left-0 w-[800px] h-[800px] bg-purple-600/5 rounded-full blur-[150px] -z-10"></div>
        <div className="max-w-7xl mx-auto px-6 flex flex-col lg:flex-row items-stretch relative z-10">
          <div className="lg:w-[40%] flex flex-col py-4">
            <div className="h-1/2 flex flex-col justify-center">
              <h1 className="text-5xl md:text-7xl lg:text-[75px] font-black leading-[0.9] tracking-tighter text-white uppercase italic">
                Future of <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-600 via-orange-400 to-amber-500">
                  Control is Here.
                </span>
              </h1>
            </div>
            <div className="h-1/2 flex flex-col justify-between pt-2">
              <div className="grid grid-cols-2 gap-6">
                <div className="p-5 h-[210px] bg-white/5 border-l-4 border-red-600 backdrop-blur-md rounded-r-xl transition-all duration-300 hover:bg-white/10 hover:scale-[1.02]">
                  <p className="text-[18px] font-black text-red-500 uppercase tracking-widest mb-1">Success Metric</p>
                  <p className="text-white text-[16px] font-bold tracking-tight">98.4% Efficiency Rate</p>
                  <p className="pt-1 text-slate-400 text-[14px] mt-1 leading-tight">Optimized every internal project pipeline to maximize team velocity.</p>
                </div>
                <div className="p-5 h-[210px] bg-white/5 border-l-4 border-amber-500 backdrop-blur-md rounded-r-xl transition-all duration-300 hover:bg-white/10 hover:scale-[1.02]">
                  <p className="text-[18px] font-black text-amber-500 uppercase tracking-widest mb-1">Global Impact</p>
                  <p className="text-white text-[16px] font-bold tracking-tight">2.4M+ Data Points</p>
                  <p className="pt-1 text-slate-400 text-[14px] mt-1 leading-tight">Information is synchronized in real-time daily across every active node.</p>
                </div>
              </div>
              <div className="flex justify-center mt-8">
                <Link href="/dashboard">
                  <Button className="relative overflow-hidden !bg-gradient-to-r !from-red-600 !to-red-800 hover:!from-amber-400 hover:!to-amber-600 text-white border border-white/20 px-10 py-4 text-lg font-bold rounded-full !shadow-[0_0_40px_rgba(220,38,38,0.5)] hover:!shadow-[0_0_60px_rgba(245,158,11,0.7)] hover:scale-105 transition-all duration-500 active:scale-95 group">
                    <span className="relative z-10 flex items-center">Launch Dashboard <span className="inline-block ml-3 group-hover:translate-x-2 transition-transform duration-300">→</span></span>
                  </Button>
                </Link>
              </div>
            </div>
          </div>
          <div className="lg:w-[60%] w-full flex items-center justify-end lg:translate-x-16 mt-16 lg:mt-0">
            <div className="relative group w-full">
              <div className="relative aspect-video w-[800px] h-[350px] md:h-[500px] rounded-[3rem] overflow-hidden shadow-[0_50px_120px_rgba(0,0,0,0.85)] border-[14px] border-white/5 bg-slate-900">
                <Image src="/bd.png" alt="Hestabit System Dashboard" fill className="object-cover contrast-[1.15]" priority />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES GRID */}
      <section className="py-24 px-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { 
              title: "Real-time Sync", 
              desc: "Engineered for zero-latency data transmission across global nodes.", 
              border: "border-red-600",
              svg: <svg className="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            },
            { 
              title: "Neural Logic", 
              desc: "Advanced predictive algorithms that adapt to your operational workflow.", 
              border: "border-purple-600",
              svg: <svg className="w-10 h-10 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
            },
            { 
              title: "Shield Security", 
              desc: "Military-grade encryption protocols protecting every bit of data.", 
              border: "border-amber-500",
              svg: <svg className="w-10 h-10 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
            }
          ].map((feat, i) => (
            <div key={i} className={`p-8 bg-white/5 border-t-4 ${feat.border} backdrop-blur-md rounded-xl hover:bg-white/10 transition-all duration-300 hover:-translate-y-2 cursor-default group`}>
              <div className="mb-6 transform group-hover:scale-110 transition-transform">{feat.svg}</div>
              <h3 className="text-xl font-bold text-white mb-4 uppercase italic tracking-tighter">{feat.title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{feat.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="py-16 bg-white/5 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { name: "Alex Rivera", role: "CTO, NexaCorp" },
              { name: "Sarah Chen", role: "Ops Director, Velo" },
              { name: "Marcus Thorne", role: "Lead Dev, Ironhold" },
              { name: "Elena Voss", role: "VP Product, Zenith" }
            ].map((user, i) => (
              <div key={i} className="p-6 bg-[#160b2e] border border-white/10 rounded-2xl shadow-xl transition-all duration-500 hover:scale-105 hover:border-purple-500/50 hover:shadow-purple-500/10 group cursor-default">
                <div className="flex text-red-500 mb-4 text-[10px] tracking-widest">★★★★★</div>
                <p className="text-slate-300 text-sm italic mb-8 leading-relaxed">
                  "Hestabit redefined our workflow. The control dashboard is beyond anything we’ve used."
                </p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-purple-600 to-blue-500 border border-white/10"></div>
                  <div>
                    <p className="text-white text-[11px] font-black uppercase tracking-tighter group-hover:text-purple-400 transition-colors">{user.name}</p>
                    <p className="text-slate-500 text-[9px] uppercase font-bold">{user.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="pt-12 pb-6 px-6 border-t border-white/5 bg-[#0a0516]">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-16 mb-20">
          <div>
            <h2 className="text-white font-black text-3xl uppercase italic mb-6 tracking-tighter">Hestabit</h2>
            <div className="space-y-2 border-l-2 border-red-600 pl-4">
              <p className="text-white text-sm font-bold uppercase">Vibhav Khaneja</p>
              <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">Trainee Software Engineer</p>
              <p className="text-red-500 text-xs font-black tracking-tighter">+91 8130907023</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-12">
            <div>
              <h4 className="text-white font-bold uppercase text-[10px] mb-6 tracking-widest opacity-50">Platform</h4>
              <ul className="text-slate-400 space-y-3 text-[11px] uppercase font-black">
                <li><Link href="#" className="hover:text-white transition">Dashboard</Link></li>
                <li><Link href="#" className="hover:text-white transition">Security</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-bold uppercase text-[10px] mb-6 tracking-widest opacity-50">Company</h4>
              <ul className="text-slate-400 space-y-3 text-[11px] uppercase font-black">
                <li><Link href="#" className="hover:text-white transition">About</Link></li>
                <li><Link href="#" className="hover:text-white transition">Contact</Link></li>
              </ul>
            </div>
          </div>
        </div>
        <div className="max-w-7xl mx-auto pt-8 border-t border-white/5 flex justify-between items-center text-[9px] text-slate-600 uppercase font-black tracking-[0.2em]">
          <p>© 2026 Hestabit Technologies. Noida, India.</p>
          <div className="flex gap-8 italic">
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
          </div>
        </div>
      </footer>
    </div>
  );
}