import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Vector Tutor — Personalised AI Tutor",
  description: "Adaptive AI learning companion for AI/ML students"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}