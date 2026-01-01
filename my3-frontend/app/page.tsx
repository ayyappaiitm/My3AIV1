import { Hero } from '@/components/landing/Hero'
import { Features } from '@/components/landing/Features'
import { Demo } from '@/components/landing/Demo'

export default function LandingPage() {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'My3 - Your AI Gift Concierge',
    description: 'Never forget a birthday again. AI-powered gift recommendations for the people who matter most.',
    url: process.env.NEXT_PUBLIC_SITE_URL || 'https://my3.app',
    applicationCategory: 'LifestyleApplication',
    operatingSystem: 'Web',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'USD',
    },
    featureList: [
      'AI-powered gift recommendations',
      'Birthday and occasion reminders',
      'Visual relationship network',
      'Personalized gift suggestions',
    ],
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      <main className="min-h-screen">
        <Hero />
        <Features />
        <Demo />
      </main>
    </>
  )
}

