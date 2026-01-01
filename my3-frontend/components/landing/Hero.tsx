'use client'

import Link from 'next/link'
import { Logo } from '@/components/ui/Logo'
import { ParallaxBackground } from './ParallaxBackground'

export function Hero() {
  return (
    <ParallaxBackground>
      <section className="min-h-screen flex flex-col items-center justify-center px-4 text-center">
        {/* Frosted glass container - similar to Edge modal */}
        <div 
          className="relative z-30 backdrop-blur-xl bg-white/90 dark:bg-gray-900/90 rounded-3xl p-8 md:p-12 max-w-4xl w-full mx-4 shadow-2xl border border-white/30"
          style={{
            backdropFilter: 'blur(24px) saturate(180%)',
            WebkitBackdropFilter: 'blur(24px) saturate(180%)',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
          }}
        >
          <div className="mb-6">
            <Logo variant="hero" showSubtitle={true} className="justify-center" />
          </div>
          <p className="text-2xl md:text-3xl text-text mb-4 max-w-2xl mx-auto font-semibold">
            Your AI-powered personal relationship and gifting concierge
          </p>
          <p className="text-lg text-text-light mb-8 max-w-xl mx-auto">
            Never forget a birthday again. Get thoughtful gift recommendations for the people who matter most.
          </p>
          <div className="flex gap-4 flex-wrap justify-center">
            <Link
              href="/register"
              className="px-8 py-3 bg-gradient-primary text-white rounded-lg font-medium hover:opacity-90 transition-opacity shadow-lg"
            >
              Get Started
            </Link>
            <Link
              href="/login"
              className="px-8 py-3 border-2 border-primary text-primary rounded-lg font-medium hover:bg-primary hover:text-white transition-colors shadow-lg"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>
    </ParallaxBackground>
  )
}

