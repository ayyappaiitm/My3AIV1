import { Hero } from '@/components/landing/Hero'
import { Features } from '@/components/landing/Features'
import { Demo } from '@/components/landing/Demo'

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      <Hero />
      <Features />
      <Demo />
    </main>
  )
}

