import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import Navbar from "@/components/ui/Navbar";
import Sidebar from "@/components/ui/Sidebar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Admin Dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {/* Dashboard Layout */}
        <div className="flex h-screen overflow-hidden bg-gray-100">
          {/* Sidebar */}
          <Sidebar />

          {/* Main Section */}
          <div className="flex flex-col flex-1">
            {/* Top Navbar */}
            <Navbar />

            {/* Page Content */}
            <main className="flex-1 p-6 bg-gray-50 overflow-y-auto">
{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
