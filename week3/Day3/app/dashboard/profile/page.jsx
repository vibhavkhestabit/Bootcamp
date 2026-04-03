import Image from "next/image";
import Link from "next/link";

export default function ProfilePage() {
  return (
    <div className="w-full min-h-screen bg-white p-6 md:p-10">
      <div className="w-full bg-white border border-blue-100 rounded-xl shadow-sm overflow-hidden mb-8">
        <div className="p-8 md:p-12 flex flex-col md:flex-row items-center md:items-start gap-10">
          <div className="w-40 h-40 md:w-52 md:h-52 relative flex-shrink-0 border-4 border-blue-50 rounded-full overflow-hidden shadow-md">
            <Image
              src="/Vibhav_Profile.jpeg"
              alt="Profile"
              fill
              className="object-cover"
            />
          </div>
          <div className="flex-grow text-center md:text-left pt-4">
            <h1 className="text-3xl font-black text-slate-800 tracking-tight uppercase">
              Vibhav Khaneja
            </h1>
            <p className="text-blue-600 font-bold text-sm tracking-widest uppercase mt-1">
              Trainee Software Engineer
            </p>
            <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              <div>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">
                  Email Address
                </p>
                <p className="text-slate-700 font-medium break-all">
                  vibhav@hestabit.com
                </p>
              </div>
              <div>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">
                  Phone Number
                </p>
                <p className="text-slate-700 font-medium">+91 8130907023</p>
              </div>
              <div>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">
                  Location
                </p>
                <p className="text-slate-700 font-medium">Noida, India</p>
              </div>
              <div>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">
                  Employee ID
                </p>
                <p className="text-slate-700 font-medium">TSE: 100</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        <div className="lg:col-span-2 bg-white border border-blue-50 rounded-xl p-8 shadow-sm">
          <h2 className="text-[18px] font-black text-slate-800 uppercase tracking-[0.3em] mb-3 border-b border-blue-50 pb-2">
            Professional Bio
          </h2>
          <p className="text-slate-600 leading-relaxed text-[16px]">
            Passionate Software Engineer Trainee with a strong focus on building
            responsive and high-performance web applications using the Next.js
            ecosystem. Dedicated to writing clean, maintainable code and
            mastering the latest frontend technologies to solve complex digital
            business problems. I'm completing my graduation from UPES Dehradun
            and currently working as a Trainee Software Engineer with Hestabit
            who have given my career a kickstart and a bright path for my
            future.
          </p>
        </div>

        <div className="bg-slate-50 border border-blue-50 rounded-xl p-8 shadow-sm">
          <h2 className="text-[18px] font-black text-slate-800 uppercase tracking-[0.3em] mb-3 border-b border-blue-100 pb-2">
            Skills & Growth
          </h2>
          <div className="space-y-6">
            <div>
              <p className="text-[18px] font-black text-slate-400 uppercase tracking-widest mb-2">
                Core Stack
              </p>
              <div className="flex flex-wrap gap-3">
                {["Next.js", "React", "Tailwind", "JavaScript"].map((skill) => (
                  <span
                    key={skill}
                    className="px-3 py-1 bg-blue-50 text-blue-700 text-[12px] font-bold rounded-full uppercase"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <p className="text-[18px] font-black text-slate-400 uppercase tracking-widest mb-1">
                Education
              </p>
              <p className="text-slate-700 text-[14px] font-bold">
                UPES Dehradun
              </p>
              <p className="text-slate-500 text-[12px] pt-1">B.Tech (Pursuing)</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-50 border border-blue-100 rounded-xl p-8 shadow-sm">
          <h2 className="text-[18px] font-black text-slate-800 uppercase tracking-[0.3em] mb-3 border-b border-blue-100 pb-2">
            Connect
          </h2>
          <div className="space-y-8">
            <Link href="#" className="flex items-center gap-3 group pt-3">
              <svg
                className="w-5 h-5 text-slate-400 group-hover:text-blue-600 transition-colors"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
              </svg>
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest group-hover:text-blue-600 transition-colors">
                LinkedIn
              </span>
            </Link>
            <Link href="#" className="flex items-center gap-3 group">
              <svg
                className="w-5 h-5 text-slate-400 group-hover:text-black transition-colors"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.045 4.126H5.078z" />
              </svg>
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest group-hover:text-black transition-colors">
                Twitter / X
              </span>
            </Link>
            <Link href="#" className="flex items-center gap-3 group">
              <svg
                className="w-5 h-5 text-slate-400 group-hover:text-slate-900 transition-colors"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
              </svg>
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest group-hover:text-slate-900 transition-colors">
                GitHub
              </span>
            </Link>
            <Link href="#" className="flex items-center gap-3 group">
              <svg
                className="w-5 h-5 text-slate-400 group-hover:text-pink-600 transition-colors"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
              </svg>
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest group-hover:text-pink-600 transition-colors">
                Instagram
              </span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
