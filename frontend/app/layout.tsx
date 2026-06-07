import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { ThemeProvider } from "next-themes";
import { QueryProvider } from "@/components/shared/query-provider";
import { ToastProvider } from "@/components/ui/use-toast";
import { Toaster } from "@/components/ui/toaster";
import "./globals.css";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Sen'Analytics Mission Control",
  description:
    "Agentic Governance Operating System — Visual AI-powered governance, compliance, security, and risk management platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geist.className} bg-mission-950 text-mission-100 antialiased`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          <QueryProvider>
            <ToastProvider>
              {children}
              <Toaster />
            </ToastProvider>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
