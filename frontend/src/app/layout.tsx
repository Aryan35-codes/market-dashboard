import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "MarketPulse — Market Intelligence Compressed",
  description:
    "Understand current market conditions in under 5 minutes. AI-powered market summary, sector analysis, options data, and smart watchlist — no noise, no predictions.",
  keywords: ["market intelligence", "nifty", "stock market", "market summary", "options analysis"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} font-sans antialiased bg-zinc-950 text-zinc-100 min-h-screen`}
      >
        {children}
      </body>
    </html>
  );
}
