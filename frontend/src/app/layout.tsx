import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Header from '@/components/Header';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AI Detector - Detect AI-Generated Images & Videos',
  description: 'Powerful AI detection tool to identify deepfakes and AI-generated content in images and videos.',
  keywords: ['AI detection', 'deepfake detection', 'AI-generated content', 'media authentication'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
          <Header />
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
