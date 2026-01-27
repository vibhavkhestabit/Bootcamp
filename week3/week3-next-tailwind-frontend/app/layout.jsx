import Navbar from "@/components/ui/Navbar";
import "@/app/globals.css";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased bg-white text-slate-900">
        <Navbar></Navbar>
        <div className="flex">
          <main className="flex-1 min-h-screen">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}