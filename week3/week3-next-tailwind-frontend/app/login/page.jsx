'use client';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Button from "@/components/ui/Button";

export default function LoginPage() {
  const router = useRouter();

  const handleSignIn = (e) => {
    e.preventDefault();
    router.push('/dashboard');
  };

  return (

    <div className="h-screen w-full relative flex items-center justify-center p-6 overflow-hidden">
      
      <div className="absolute inset-0 bg-gradient-to-br from-[#00d2ff] via-[#9d50bb] to-[#ff00c8] -z-20"></div>
      
      <div className="absolute -top-[10%] -left-[10%] w-[700px] h-[700px] bg-[#3a7bd5] rounded-full blur-[120px] opacity-60 mix-blend-screen -z-10 animate-pulse"></div>
      <div className="absolute -bottom-[10%] -right-[10%] w-[600px] h-[600px] bg-[#f000ff] rounded-full blur-[120px] opacity-50 mix-blend-screen -z-10 animate-pulse" style={{ animationDelay: '2s' }}></div>

      <div className="w-full max-w-[420px] bg-white/70 backdrop-blur-2xl rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.2)] border border-white/50 p-10 z-10">
        <div className="mb-10 text-center">
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Login</h1>
          <p className="text-slate-500 text-sm mt-2 font-medium">Welcome back to Hestabit</p>
        </div>

        <form className="space-y-5" onSubmit={handleSignIn}>
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-600 uppercase tracking-widest ml-1">Email Address</label>
            <input 
              required
              type="email" 
              className="w-full px-4 py-3 bg-white/50 border border-slate-200 rounded-xl text-slate-900 text-sm focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none" 
              placeholder="name@company.com" 
            />
          </div>
          
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-600 uppercase tracking-widest ml-1">Password</label>
            <input 
              required
              type="password" 
              className="w-full px-4 py-3 bg-white/50 border border-slate-200 rounded-xl text-slate-900 text-sm focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none" 
              placeholder="••••••••" 
            />
            <div className="flex justify-end pr-1">
              <Link href="#" className="text-xs text-indigo-600 font-bold hover:text-indigo-800 transition-colors">
                Forgot password?
              </Link>
            </div>
          </div>

          <Button 
            onClick={handleSignIn}
            className="w-full !bg-slate-900 hover:!bg-slate-800 text-white py-4 rounded-xl text-sm font-bold shadow-xl shadow-blue-900/10 transition-all mt-4 active:scale-[0.98]"
          >
            Sign In
          </Button>
        </form>

        <div className="relative my-8">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-200"></div></div>
          <div className="relative flex justify-center text-[10px] uppercase tracking-widest font-bold text-slate-400">
            <span className="bg-transparent px-4">Or continue with</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <button className="flex items-center justify-center py-3 bg-white/80 border border-white rounded-xl hover:bg-white transition-all shadow-sm">
            <svg className="w-5 h-5" viewBox="0 0 24 24"><path fill="#EA4335" d="M24 4.5v15c0 .85-.65 1.5-1.5 1.5H21V7.39l-9 5.58-9-5.58V21H1.5C.65 21 0 20.35 0 19.5v-15c0-.42.17-.8.44-1.1L12 9.3l11.56-5.9c.27.3.44.68.44 1.1z"/></svg>
          </button>
          <button className="flex items-center justify-center py-3 bg-white/80 border border-white rounded-xl hover:bg-white transition-all shadow-sm">
            <svg className="w-5 h-5" fill="#1877F2" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
          </button>
          <button className="flex items-center justify-center py-3 bg-white/80 border border-white rounded-xl hover:bg-white transition-all shadow-sm">
            <svg className="w-5 h-5" fill="#181717" viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
          </button>
        </div>
      </div>
    </div>
  );
}