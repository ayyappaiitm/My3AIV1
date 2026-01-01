# Parallax Background - Step-by-Step Implementation Guide

## Quick Start

This guide provides exact prompts and code snippets to implement the parallax background effect similar to Microsoft Edge Year in Review.

---

## Story 1: Analyze Current Implementation ✅

**Status:** Already completed during assessment

**Findings:**
- Landing page: `my3-frontend/app/page.tsx`
- Hero component: `my3-frontend/components/landing/Hero.tsx` (already 'use client')
- Current background: `bg-background` (#FFF9F5)
- Integration point: Wrap Hero content in ParallaxBackground

**Action:** Proceed to Story 2

---

## Story 2: Build ParallaxBackground Component

### Step 2.1: Create Component File

**File:** `my3-frontend/components/landing/ParallaxBackground.tsx`

### Step 2.2: Implementation Code

```tsx
'use client'

import { useRef, useEffect, useState, useCallback } from 'react'

interface ParallaxBackgroundProps {
  children: React.ReactNode
}

export function ParallaxBackground({ children }: ParallaxBackgroundProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const parallaxRef = useRef<HTMLDivElement>(null)
  const mousePosition = useRef({ x: 0, y: 0 })
  const animationFrameId = useRef<number | null>(null)
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  // Check for reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  // Mouse move handler with requestAnimationFrame
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!containerRef.current || prefersReducedMotion) return

    const rect = containerRef.current.getBoundingClientRect()
    const x = (e.clientX - rect.left) / rect.width - 0.5
    const y = (e.clientY - rect.top) / rect.height - 0.5

    mousePosition.current = { x, y }

    // Cancel previous frame
    if (animationFrameId.current !== null) {
      cancelAnimationFrame(animationFrameId.current)
    }

    // Schedule update
    animationFrameId.current = requestAnimationFrame(() => {
      if (parallaxRef.current && !prefersReducedMotion) {
        // Inverse parallax: move opposite to cursor
        const translateX = -mousePosition.current.x * 30
        const translateY = -mousePosition.current.y * 30

        parallaxRef.current.style.transform = `translate3d(${translateX}px, ${translateY}px, 0)`
      }
    })
  }, [prefersReducedMotion])

  // Attach mouse listener
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    container.addEventListener('mousemove', handleMouseMove)
    return () => {
      container.removeEventListener('mousemove', handleMouseMove)
      if (animationFrameId.current !== null) {
        cancelAnimationFrame(animationFrameId.current)
      }
    }
  }, [handleMouseMove])

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
        ref={parallaxRef}
        className="absolute inset-0 pointer-events-none"
        style={{
          willChange: prefersReducedMotion ? 'auto' : 'transform',
        }}
      >
        {/* Layers will be added in Story 3 */}
      </div>

      {/* Content foreground */}
      <div className="relative z-20 flex items-center justify-center">
        {children}
      </div>
    </div>
  )
}
```

### Step 2.3: Test Basic Component

1. Import in Hero component temporarily
2. Verify gradient renders
3. Check mouse movement (should see subtle movement)
4. Test with reduced motion preference

---

## Story 3: Add Parallax Image Layers

### Step 3.1: Create Placeholder Images

**Directory:** `my3-frontend/public/images/parallax/`

Create these SVG files:

**1. `bg-network.svg`** (Background layer, depth: -35)
```svg
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="grad1" cx="50%" cy="50%">
      <stop offset="0%" style="stop-color:#FF6B6B;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#FF6B6B;stop-opacity:0" />
    </radialGradient>
  </defs>
  <circle cx="200" cy="150" r="80" fill="url(#grad1)" />
  <circle cx="600" cy="300" r="60" fill="url(#grad1)" />
  <circle cx="400" cy="450" r="70" fill="url(#grad1)" />
  <line x1="200" y1="150" x2="400" y2="450" stroke="#FF6B6B" stroke-width="2" opacity="0.2" />
  <line x1="600" y1="300" x2="400" y2="450" stroke="#FF6B6B" stroke-width="2" opacity="0.2" />
</svg>
```

**2. `bg-calendar.svg`** (Mid-back layer, depth: -20)
```svg
<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
  <rect x="50" y="50" width="500" height="300" rx="10" fill="none" stroke="#14B8A6" stroke-width="3" opacity="0.4" />
  <circle cx="150" cy="150" r="8" fill="#14B8A6" opacity="0.5" />
  <circle cx="300" cy="150" r="8" fill="#14B8A6" opacity="0.5" />
  <circle cx="450" cy="150" r="8" fill="#14B8A6" opacity="0.5" />
  <line x1="50" y1="200" x2="550" y2="200" stroke="#14B8A6" stroke-width="2" opacity="0.3" />
</svg>
```

**3. `bg-gifts.svg`** (Mid layer, depth: -10)
```svg
<svg width="500" height="500" xmlns="http://www.w3.org/2000/svg">
  <rect x="150" y="100" width="200" height="200" rx="5" fill="#FF6B6B" opacity="0.4" />
  <polygon points="150,100 250,50 350,100" fill="#FFA07A" opacity="0.5" />
  <circle cx="200" cy="200" r="15" fill="#14B8A6" opacity="0.6" />
  <circle cx="300" cy="200" r="15" fill="#14B8A6" opacity="0.6" />
</svg>
```

**4. `bg-people.svg`** (Foreground layer, depth: 0)
```svg
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
  <circle cx="200" cy="150" r="50" fill="#FF6B6B" opacity="0.3" />
  <circle cx="150" cy="250" r="40" fill="#14B8A6" opacity="0.3" />
  <circle cx="250" cy="250" r="40" fill="#8B5CF6" opacity="0.3" />
  <line x1="200" y1="200" x2="150" y2="210" stroke="#FF6B6B" stroke-width="3" opacity="0.4" />
  <line x1="200" y1="200" x2="250" y2="210" stroke="#FF6B6B" stroke-width="3" opacity="0.4" />
</svg>
```

### Step 3.2: Update ParallaxBackground Component

Add this interface and update the component:

```tsx
interface ParallaxLayerProps {
  depth: number
  image: string
  className?: string
  style?: React.CSSProperties
}

function ParallaxLayer({ depth, image, className = '', style = {} }: ParallaxLayerProps) {
  const layerRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = containerRef.current?.closest('[data-parallax-container]')
    if (!container || !layerRef.current) return

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect()
      const x = (e.clientX - rect.left) / rect.width - 0.5
      const y = (e.clientY - rect.top) / rect.height - 0.5

      // Inverse parallax: deeper layers move less
      const intensity = Math.abs(depth) / 35 // Normalize to 0-1
      const translateX = -x * 30 * intensity
      const translateY = -y * 30 * intensity

      layerRef.current!.style.transform = `translate3d(${translateX}px, ${translateY}px, 0)`
    }

    container.addEventListener('mousemove', handleMouseMove)
    return () => container.removeEventListener('mousemove', handleMouseMove)
  }, [depth])

  return (
    <div
      ref={layerRef}
      className={`absolute ${className}`}
      style={{
        willChange: 'transform',
        transition: prefersReducedMotion ? 'none' : 'transform 0.1s ease-out',
        ...style,
      }}
    >
      <img
        src={image}
        alt=""
        aria-hidden="true"
        className="w-full h-full object-contain opacity-40"
        style={{ maxWidth: '100%', height: 'auto' }}
      />
    </div>
  )
}
```

### Step 3.3: Add Layers to ParallaxBackground

Update the parallax container div:

```tsx
<div
  ref={parallaxRef}
  className="absolute inset-0 pointer-events-none"
  data-parallax-container
  style={{
    willChange: prefersReducedMotion ? 'auto' : 'transform',
  }}
>
  {/* Background layer */}
  <ParallaxLayer
    depth={-35}
    image="/images/parallax/bg-network.svg"
    className="top-0 left-0 w-96 md:w-[500px]"
  />

  {/* Mid-back layer */}
  <ParallaxLayer
    depth={-20}
    image="/images/parallax/bg-calendar.svg"
    className="bottom-0 right-0 w-64 md:w-80"
  />

  {/* Mid layer */}
  <ParallaxLayer
    depth={-10}
    image="/images/parallax/bg-gifts.svg"
    className="top-1/4 right-1/4 w-48 md:w-64"
  />

  {/* Foreground layer */}
  <ParallaxLayer
    depth={0}
    image="/images/parallax/bg-people.svg"
    className="bottom-1/4 left-1/4 w-40 md:w-56"
  />
</div>
```

---

## Story 4: Wire into Landing Page

### Step 4.1: Update Hero Component

**File:** `my3-frontend/components/landing/Hero.tsx`

```tsx
'use client'

import Link from 'next/link'
import { Logo } from '@/components/ui/Logo'
import { ParallaxBackground } from './ParallaxBackground'

export function Hero() {
  return (
    <ParallaxBackground>
      <section className="min-h-screen flex flex-col items-center justify-center px-4 text-center">
        <div className="mb-6">
          <Logo variant="hero" showSubtitle={true} className="justify-center" />
        </div>
        <p className="text-2xl md:text-3xl text-text mb-4 max-w-2xl">
          Your AI-powered personal relationship and gifting concierge
        </p>
        <p className="text-lg text-text-light mb-8 max-w-xl">
          Never forget a birthday again. Get thoughtful gift recommendations for the people who matter most.
        </p>
        <div className="flex gap-4 flex-wrap justify-center">
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
    </ParallaxBackground>
  )
}
```

### Step 4.2: Update Main Page (Remove Background)

**File:** `my3-frontend/app/page.tsx`

```tsx
// ... existing code ...

<main className="min-h-screen"> {/* Remove bg-background - ParallaxBackground handles it */}
  <Hero />
  <Features />
  <Demo />
</main>
```

### Step 4.3: Add Mobile Responsiveness

Update ParallaxBackground to disable/reduce on mobile:

```tsx
// In ParallaxBackground component, add:
const [isMobile, setIsMobile] = useState(false)

useEffect(() => {
  const checkMobile = () => {
    setIsMobile(window.innerWidth < 768)
  }
  checkMobile()
  window.addEventListener('resize', checkMobile)
  return () => window.removeEventListener('resize', checkMobile)
}, [])

// In handleMouseMove, add:
if (isMobile || prefersReducedMotion) return
```

---

## Story 5: Image Specifications for Nanobanana

### Image Spec Document

**File:** `NANOBANANA_IMAGE_SPECS.md`

```markdown
# Parallax Background Images - Nanobanana Specifications

## Layer 1: Background Network (Depth: -35)
- **Name:** "Relationship Network Background"
- **Size:** 1200x800px
- **Aspect Ratio:** 3:2
- **Position:** Top-left, behind all content
- **Description:** Abstract, soft-focus illustration of interconnected nodes/people in a network. Very subtle, dreamy aesthetic. Colors: soft coral (#FF6B6B at 30% opacity) and teal (#14B8A6 at 20% opacity) gradients. Blurred edges, no sharp lines. Should feel like a gentle background glow.
- **Style:** Watercolor/soft gradient, minimal detail, high blur
- **Opacity in design:** 0.3

## Layer 2: Calendar/Occasions (Depth: -20)
- **Name:** "Occasions Timeline"
- **Size:** 800x600px
- **Aspect Ratio:** 4:3
- **Position:** Bottom-right corner
- **Description:** Stylized calendar or timeline showing special dates (birthdays, anniversaries). Clean, modern illustration. Use My3 brand colors: coral accents on soft cream background. Include subtle icons (cake, gift, heart). Semi-transparent, should not compete with text.
- **Style:** Modern flat design, clean lines, icon-based
- **Opacity in design:** 0.4

## Layer 3: Gift Suggestions (Depth: -10)
- **Name:** "Smart Gift Box"
- **Size:** 600x600px
- **Aspect Ratio:** 1:1
- **Position:** Center-right, mid-level
- **Description:** Elegant gift box or wrapped present with a subtle "AI sparkle" effect. Could include a small tag or ribbon. Colors: primary coral (#FF6B6B) with teal (#14B8A6) accents. Should feel premium but not overwhelming.
- **Style:** 3D isometric or flat illustration, premium feel
- **Opacity in design:** 0.5

## Layer 4: People/Relationships (Depth: 0)
- **Name:** "Connected People"
- **Size:** 500x500px
- **Aspect Ratio:** 1:1
- **Position:** Top-right, near but not overlapping hero text
- **Description:** Simple, friendly illustration of 2-3 people connected (could be holding hands, or connected by lines). Very minimal, icon-like. Use My3 colors with high transparency. Should feel warm and personal.
- **Style:** Minimalist icon style, friendly, approachable
- **Opacity in design:** 0.4

## Layer 5 (Optional): Celebration Elements (Depth: +10)
- **Name:** "Celebration Sparkles"
- **Size:** 400x400px
- **Aspect Ratio:** 1:1
- **Position:** Scattered, very subtle
- **Description:** Small sparkles, stars, or celebration elements. Very light, scattered pattern. Use brand colors at very low opacity. Should add life without distraction.
- **Style:** Minimal sparkle/star shapes, scattered
- **Opacity in design:** 0.2

## Color Palette Reference
- Primary Coral: #FF6B6B
- Light Coral: #FFA07A
- Teal: #14B8A6
- Background Cream: #FFF9F5
- Accent Purple: #8B5CF6 (for depth)

## Technical Requirements
- Format: PNG with transparency (or SVG)
- Export: WebP preferred for web, PNG fallback
- File size: Each image < 200KB optimized
- Resolution: 2x for retina displays
```

---

## Story 6: Accessibility & Performance Polish

### Final ParallaxBackground Component

See the complete optimized component in the implementation. Key additions:

1. **Reduced Motion Support:**
```tsx
const prefersReducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)')
```

2. **Performance Optimization:**
```tsx
// Use refs instead of state
const mousePosition = useRef({ x: 0, y: 0 })

// requestAnimationFrame for smooth updates
animationFrameId.current = requestAnimationFrame(() => {
  // Apply transforms
})
```

3. **GPU Acceleration:**
```tsx
style={{ transform: `translate3d(${x}px, ${y}px, 0)` }}
```

4. **Mobile Optimization:**
```tsx
const isMobile = window.innerWidth < 768
if (isMobile) {
  // Disable or reduce parallax
}
```

---

## Testing Checklist

- [ ] Parallax works smoothly on desktop
- [ ] Reduced motion preference is respected
- [ ] Mobile view works (parallax disabled/reduced)
- [ ] Text remains readable
- [ ] Images don't overlap hero content
- [ ] Performance: 60fps on modern browsers
- [ ] No layout shifts
- [ ] Works in Chrome, Firefox, Safari, Edge
- [ ] Accessibility: Screen readers ignore decorative images
- [ ] Lighthouse score > 90

---

## Troubleshooting

### Issue: Parallax feels janky
**Solution:** Ensure using `requestAnimationFrame` and `translate3d`

### Issue: Images cause layout shift
**Solution:** Set fixed width/height on images, use Next.js Image component

### Issue: Performance issues on mobile
**Solution:** Disable parallax below 768px breakpoint

### Issue: Text not readable
**Solution:** Reduce image opacity, add text shadow, adjust gradient

---

## Next Steps After Implementation

1. Generate images with Nanobanana using specs
2. Replace placeholder SVGs
3. Optimize images (compress, convert to WebP)
4. Test on real devices
5. Gather user feedback
6. Iterate on positioning/opacity

---

**Ready to implement? Start with Story 2 and work sequentially!** 🚀

