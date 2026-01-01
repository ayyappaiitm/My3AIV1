'use client'

import { useRef, useEffect, useState } from 'react'

interface ParallaxBackgroundProps {
  children: React.ReactNode
}

interface ParallaxLayerProps {
  depth: number
  image: string
  className?: string
  style?: React.CSSProperties
  alt?: string
}

function ParallaxLayer({ 
  depth, 
  image, 
  className = '', 
  style = {}, 
  alt = '',
  containerRef,
  prefersReducedMotion,
  isMobile
}: ParallaxLayerProps & { 
  containerRef: React.RefObject<HTMLDivElement>
  prefersReducedMotion: boolean
  isMobile: boolean
}) {
  const layerRef = useRef<HTMLDivElement>(null)
  const animationFrameId = useRef<number | null>(null)

  // Mouse move handler for this layer
  useEffect(() => {
    const container = containerRef.current
    if (!container || !layerRef.current || prefersReducedMotion || isMobile) return

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect()
      const x = (e.clientX - rect.left) / rect.width - 0.5
      const y = (e.clientY - rect.top) / rect.height - 0.5

      // Inverse parallax: deeper layers move less
      // Edge website uses very pronounced movement (100-120px range)
      // Depth values: -60 (deepest) to 0 (foreground)
      // Normalize depth to 0-1 range, with 0 (foreground) getting max movement
      const normalizedDepth = depth === 0 ? 0 : Math.abs(depth) // 0 to 60
      const maxDepth = 60 // Deepest layer depth
      const baseIntensity = depth === 0 ? 1.0 : 1 - (normalizedDepth / maxDepth) // 0 to 1, inverted
      const maxMovement = 120 // Very pronounced movement like Edge website
      const translateX = -x * maxMovement * baseIntensity
      const translateY = -y * maxMovement * baseIntensity

      // Cancel previous frame
      if (animationFrameId.current !== null) {
        cancelAnimationFrame(animationFrameId.current)
      }

      // Schedule update
      animationFrameId.current = requestAnimationFrame(() => {
        if (layerRef.current) {
          layerRef.current.style.transform = `translate3d(${translateX}px, ${translateY}px, 0)`
        }
      })
    }

    container.addEventListener('mousemove', handleMouseMove)
    return () => {
      container.removeEventListener('mousemove', handleMouseMove)
      if (animationFrameId.current !== null) {
        cancelAnimationFrame(animationFrameId.current)
      }
    }
  }, [depth, prefersReducedMotion, isMobile, containerRef])

  return (
    <div
      ref={layerRef}
      className={`absolute ${className}`}
      style={{
        willChange: prefersReducedMotion || isMobile ? 'auto' : 'transform',
        transition: prefersReducedMotion ? 'none' : 'transform 0.1s ease-out',
        ...style,
      }}
    >
      <img
        src={image}
        alt={alt}
        className="opacity-50"
        style={{ maxWidth: '100%', height: 'auto', display: 'block' }}
        aria-hidden="true"
        loading="lazy"
      />
    </div>
  )
}

export function ParallaxBackground({ children }: ParallaxBackgroundProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  // Check for reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    checkMobile()

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    window.addEventListener('resize', checkMobile)

    return () => {
      mediaQuery.removeEventListener('change', handleChange)
      window.removeEventListener('resize', checkMobile)
    }
  }, [])

  return (
    <div
      ref={containerRef}
      className="relative min-h-screen overflow-hidden"
      style={{
        background: `
          radial-gradient(circle at 20% 50%, rgba(255, 107, 107, 0.15) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(20, 184, 166, 0.15) 0%, transparent 50%),
          radial-gradient(circle at 40% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
          linear-gradient(135deg, #FFF9F5 0%, #F0F9FF 100%)
        `,
      }}
    >
      {/* Parallax layers container */}
      <div
        className="absolute inset-0 pointer-events-none"
        data-parallax-container
        style={{
          willChange: prefersReducedMotion || isMobile ? 'auto' : 'transform',
        }}
      >
        {/* Background layers (deepest, move least) */}
        <ParallaxLayer
          depth={-60}
          image="/images/parallax/photo-network.svg"
          className="top-0 left-0 w-80 md:w-[600px]"
          alt=""
          containerRef={containerRef}
          prefersReducedMotion={prefersReducedMotion}
          isMobile={isMobile}
        />

        <ParallaxLayer
          depth={-55}
          image="/images/parallax/photo-calendar.svg"
          className="bottom-0 right-0 w-72 md:w-[550px]"
          alt=""
          containerRef={containerRef}
          prefersReducedMotion={prefersReducedMotion}
          isMobile={isMobile}
        />

        {/* Mid-back layers */}
        <ParallaxLayer
          depth={-45}
          image="/images/parallax/photo-people.svg"
          className="top-1/3 left-0 w-64 md:w-[500px]"
          alt=""
          containerRef={containerRef}
          prefersReducedMotion={prefersReducedMotion}
          isMobile={isMobile}
        />

        <ParallaxLayer
          depth={-40}
          image="/images/parallax/photo-reminder.svg"
          className="bottom-1/3 right-1/4 w-56 md:w-[450px]"
          alt=""
          containerRef={containerRef}
          prefersReducedMotion={prefersReducedMotion}
          isMobile={isMobile}
        />

        {/* Mid layers */}
        <ParallaxLayer
          depth={-30}
          image="/images/parallax/photo-birthday.svg"
          className="top-1/4 right-0 w-60 md:w-[480px]"
          alt=""
          containerRef={containerRef}
          prefersReducedMotion={prefersReducedMotion}
          isMobile={isMobile}
        />

        <ParallaxLayer
          depth={-25}
          image="/images/parallax/photo-anniversary.svg"
          className="bottom-1/4 left-1/3 w-58 md:w-[500px]"
          alt=""
          containerRef={containerRef}
          prefersReducedMotion={prefersReducedMotion}
          isMobile={isMobile}
        />

        <ParallaxLayer
          depth={-20}
          image="/images/parallax/photo-gift-box.svg"
          className="top-1/2 right-1/3 w-64 md:w-[550px]"
          alt=""
          containerRef={containerRef}
          prefersReducedMotion={prefersReducedMotion}
          isMobile={isMobile}
        />

        {/* Foreground layers (move most) */}
        <ParallaxLayer
          depth={-10}
          image="/images/parallax/photo-celebration.svg"
          className="top-0 right-1/4 w-52 md:w-[450px]"
          alt=""
          containerRef={containerRef}
          prefersReducedMotion={prefersReducedMotion}
          isMobile={isMobile}
        />

        <ParallaxLayer
          depth={-5}
          image="/images/parallax/photo-birthday.svg"
          className="bottom-0 left-1/4 w-56 md:w-[480px]"
          alt=""
          containerRef={containerRef}
          prefersReducedMotion={prefersReducedMotion}
          isMobile={isMobile}
        />

        <ParallaxLayer
          depth={0}
          image="/images/parallax/photo-gift-box.svg"
          className="top-1/3 left-1/2 w-50 md:w-[420px]"
          alt=""
          containerRef={containerRef}
          prefersReducedMotion={prefersReducedMotion}
          isMobile={isMobile}
        />
      </div>

      {/* Content foreground */}
      <div className="relative z-20 flex items-center justify-center">
        {children}
      </div>
    </div>
  )
}

