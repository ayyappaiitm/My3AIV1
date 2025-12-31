'use client'

import Image from 'next/image'
import Link from 'next/link'
import { useState } from 'react'

interface LogoProps {
  variant?: 'header' | 'hero' | 'auth'
  showSubtitle?: boolean
  className?: string
}

export function Logo({ variant = 'header', showSubtitle = false, className = '' }: LogoProps) {
  const [imageError, setImageError] = useState(false)
  const isHeader = variant === 'header'
  const isHero = variant === 'hero'
  const isAuth = variant === 'auth'

  // Size configurations
  const sizes = {
    header: { logo: 40, text: 'text-2xl' },
    hero: { logo: 120, text: 'text-6xl md:text-8xl' },
    auth: { logo: 60, text: 'text-4xl' },
  }

  const config = sizes[variant]

  return (
    <Link href="/" className={`flex items-center gap-3 ${className}`}>
      {/* Logo Image - Only show if image exists and no error */}
      {!imageError && (
        <div className="flex-shrink-0" style={{ width: config.logo, height: config.logo }}>
          <Image
            src="/logo.svg"
            alt="My3 Logo"
            width={config.logo}
            height={config.logo}
            priority
            className="w-full h-full object-contain"
            onError={() => setImageError(true)}
          />
        </div>
      )}

      {/* Text */}
      <div className="flex flex-col">
        <h1
          className={`font-bold bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] bg-clip-text text-transparent ${
            isHeader ? 'text-2xl' : isHero ? 'text-6xl md:text-8xl' : 'text-4xl'
          }`}
        >
          My3
        </h1>
        {showSubtitle && (
          <p
            className={`text-gray-600 ${
              isHeader ? 'text-xs' : isHero ? 'text-xl md:text-2xl' : 'text-sm'
            }`}
          >
            Your Gifting Concierge
          </p>
        )}
      </div>
    </Link>
  )
}

