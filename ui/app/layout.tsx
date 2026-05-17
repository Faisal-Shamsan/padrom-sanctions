import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/query-provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PADROM Sanctions Screening",
  description: "EU and UN sanctions screening for insurance counterparties",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>
          {/* Sidebar — full navigation will be implemented in a future sprint */}
          <div className="flex min-h-screen">
            <aside className="w-64 shrink-0 border-r bg-slate-50 p-4">
              <p className="text-sm font-semibold text-slate-800">PADROM</p>
              <p className="text-xs text-slate-500">Sanctions Screening</p>
              <nav className="mt-6 space-y-1 text-xs text-slate-500">
                {/* Navigation links go here */}
              </nav>
            </aside>
            <main className="flex-1 p-8">{children}</main>
          </div>
        </QueryProvider>
      </body>
    </html>
  );
}
