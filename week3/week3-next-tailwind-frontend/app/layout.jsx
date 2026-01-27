import Navbar from "@/components/ui/Navbar";
import Sidebar from "@/components/ui/Sidebar";
import "./globals.css";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-100">
        <Navbar />

        <div className="flex">
          <Sidebar />

          <main className="flex-1 min-h-screen p-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
