import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'
import { Analytics } from '@vercel/analytics/react'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    default: 'My3 - Your AI Gift Concierge',
    template: '%s | My3',
  },
  description: 'Never forget a birthday again. AI-powered gift recommendations for the people who matter most. Remember every occasion and find perfect gifts through natural conversation.',
  keywords: ['gift ideas', 'birthday reminder', 'AI assistant', 'gift concierge', 'personalized gifts', 'occasion tracking'],
  authors: [{ name: 'My3 Team' }],
  creator: 'My3',
  publisher: 'My3',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  openGraph: {
    title: 'My3 - Your AI Gift Concierge',
    description: 'Never forget a birthday again. AI-powered gift recommendations for the people who matter most.',
    type: 'website',
    siteName: 'My3',
    locale: 'en_US',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'My3 - Your AI Gift Concierge',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'My3 - Your AI Gift Concierge',
    description: 'Never forget a birthday again. AI-powered gift recommendations for the people who matter most.',
    images: ['/og-image.png'],
    creator: '@my3app',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    // Add when you have Google Search Console verification
    // google: 'your-verification-code',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ErrorBoundary>
          <Providers>{children}</Providers>
        </ErrorBoundary>
        <Analytics />
      </body>
    </html>
  )
}

