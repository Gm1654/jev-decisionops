import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JEV DecisionOps",
  description: "Structured invoice decision engine powered by TypeSafe JEV",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
