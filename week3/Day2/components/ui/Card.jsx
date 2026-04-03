export default function Card({ title, children, footer, color = "default" }) {
const variants = {
  primary: { border: "border-indigo-700", icon: "bg-blue-100 text-blue-700" }, 
  warning: { border: "border-yellow-500", icon: "bg-yellow-50 text-yellow-600" },
  success: { border: "border-green-600", icon: "bg-green-50 text-green-600" },
  danger: { border: "border-red-600", icon: "bg-red-50 text-red-600" },
};

  const active = variants[color] || variants.default;

  return (
    <div className={`bg-white rounded-lg shadow-sm border-t-4 ${active.border} border-x border-b border-gray-100 overflow-hidden transition-all duration-300 hover:shadow-md hover:-translate-y-1`}>
      <div className="p-5">
        <div className="flex items-center justify-between mb-4">
          <span className="text-[11px] font-bold uppercase tracking-widest text-slate-400">{title}</span>
          <div className={`w-7 h-7 rounded-full flex items-center justify-center text-[10px] ${active.icon}`}>
            ✦
          </div>
        </div>
        <div className="text-2xl font-bold text-slate-800 tracking-tight">
          {children}
        </div>
      </div>
      
      {footer && (
        <div className="px-5 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[11px] font-semibold text-blue-600 hover:text-blue-700 cursor-pointer transition">
          {footer}
          <span className="text-sm">→</span>
        </div>
      )}
    </div>
  );
}