import type { Metadata } from "next";
import { nunito } from "./fonts/fonts";
import "./globals.css";

import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";

export const metadata: Metadata = {
  title: "AI Document Assistant",
  description: "Improve your documents with AI suggestions",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${nunito.variable} ${nunito.variable} antialiased`}
    >
      <body suppressHydrationWarning className={`${nunito.className} min-h-screen flex flex-col`}>
        <Header />
        <main suppressHydrationWarning className="flex-grow container mx-auto px-4 py-8">
          {children}
        </main>
        <Footer/>
      </body>
    </html>
  );
}