'use client'

import Link from 'next/link'

export function Hero() {
  return (
    <section className="min-h-screen flex flex-col items-center justify-center px-4 text-center">
      <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-primary bg-clip-text text-transparent">
        My3
      </h1>
      <p className="text-2xl md:text-3xl text-text mb-4 max-w-2xl">
        Your AI-powered personal relationship and gifting concierge
      </p>
      <p className="text-lg text-text-light mb-8 max-w-xl">
        Never forget a birthday again. Get thoughtful gift recommendations for the people who matter most.
      </p>
      <div className="flex gap-4">
        <Link
          href="/register"
          className="px-8 py-3 bg-gradient-primary text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
        >
          Get Started
        </Link>
        <Link
          href="/login"
          className="px-8 py-3 border-2 border-primary text-primary rounded-lg font-medium hover:bg-primary hover:text-white transition-colors"
        >
          Sign In
        </Link>
      </div>
    </section>
  )
}

