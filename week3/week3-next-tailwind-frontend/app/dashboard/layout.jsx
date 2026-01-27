import Sidebar from "@/components/ui/Sidebar";

export default function DashboardLayout({ children }) {
  return (
    <div className="flex">
      {/* Sidebar only appears inside the dashboard folder routes */}
      <Sidebar />
      <main className="flex-1 min-h-screen p-6">
        {children}
      </main>
    </div>
  );
}