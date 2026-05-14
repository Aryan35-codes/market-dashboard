import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "GyanDheesh — Market Intelligence Compressed",
  description:
    "GyanDheesh provides high-signal market intelligence. Understand Indian markets in under 5 minutes with AI-powered summaries, sector analysis, and smart watchlists.",
  keywords: [
    "GyanDheesh",
    "market intelligence",
    "nifty 50",
    "bank nifty",
    "market compression",
    "AI market analysis",
    "Indian stock market",
  ],
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
