'use client'

import { useCallback, useEffect, useState } from 'react'
import Particles from '@tsparticles/react'
import { loadSlim } from '@tsparticles/slim'
import { loadLinksInteraction } from '@tsparticles/interaction-particles-links'
import { loadExternalConnectInteraction } from '@tsparticles/interaction-external-connect'
import type { Engine } from '@tsparticles/engine'

export function AnimatedBackground() {
  const [isReady, setIsReady] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const particlesInit = useCallback(async (engine: Engine) => {
    try {
      console.log('AnimatedBackground: Initializing particles...')
      // Load the slim bundle which includes basic features
      await loadSlim(engine)
      // Load links plugin for particle connections
      await loadLinksInteraction(engine)
      // Load external connect plugin for hover interactions
      await loadExternalConnectInteraction(engine)
      console.log('AnimatedBackground: Particles initialized successfully')
      setIsReady(true)
    } catch (err) {
      console.error('AnimatedBackground: Failed to initialize particles', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }, [])

  useEffect(() => {
    console.log('AnimatedBackground: Component mounted')
    return () => {
      console.log('AnimatedBackground: Component unmounted')
    }
  }, [])

  // Fallback gradient background if particles fail
  if (error) {
    console.warn('AnimatedBackground: Using fallback background due to error:', error)
    return (
      <div 
        className="absolute inset-0 w-full h-full" 
        style={{ 
          zIndex: 0,
          background: 'linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 160, 122, 0.1) 50%, rgba(20, 184, 166, 0.1) 100%)',
          opacity: 0.3
        }}
      />
    )
  }

  return (
    <div className="absolute inset-0 w-full h-full" style={{ zIndex: 0 }}>
      {!isReady && (
        <div 
          className="absolute inset-0 w-full h-full" 
          style={{ 
            background: 'linear-gradient(135deg, rgba(255, 107, 107, 0.05) 0%, rgba(255, 160, 122, 0.05) 50%, rgba(20, 184, 166, 0.05) 100%)',
            zIndex: 0
          }}
        />
      )}
      <Particles
        id="tsparticles"
        init={particlesInit}
        options={{
          background: {
            color: {
              value: 'transparent',
            },
          },
          fpsLimit: 60,
          interactivity: {
            events: {
              onClick: {
                enable: false,
              },
              onHover: {
                enable: true,
                mode: 'connect',
              },
              resize: true,
            },
            modes: {
              connect: {
                distance: 150,
                links: {
                  opacity: 0.3,
                },
                radius: 200,
              },
            },
          },
          particles: {
            color: {
              value: ['#FF6B6B', '#FFA07A', '#14B8A6'],
            },
            links: {
              color: '#FF6B6B',
              distance: 150,
              enable: true,
              opacity: 0.3,
              width: 1,
            },
            move: {
              direction: 'none',
              enable: true,
              outModes: {
                default: 'bounce',
              },
              random: true,
              speed: 1.5,
              straight: false,
            },
            number: {
              density: {
                enable: true,
                area: 800,
              },
              value: 60,
            },
            opacity: {
              value: 0.5,
              animation: {
                enable: true,
                speed: 0.5,
                sync: false,
              },
            },
            shape: {
              type: 'circle',
            },
            size: {
              value: { min: 2, max: 4 },
              animation: {
                enable: true,
                speed: 2,
                sync: false,
              },
            },
          },
          detectRetina: true,
        }}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          zIndex: 0,
        }}
      />
    </div>
  )
}

