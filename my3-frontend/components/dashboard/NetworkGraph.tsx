'use client'

import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { Recipient, Occasion, GiftIdea } from '@/lib/types'
import { apiClient } from '@/lib/api/client'
import { RecipientModal } from './RecipientModal'

interface NetworkGraphProps {
  recipients: Recipient[]
  activeRecipientId?: string | null
  onNodeClick?: (recipient: Recipient) => void
  isTyping?: boolean
}

interface RecipientDetail {
  id: string
  user_id: string
  name: string
  relationship?: string
  age_band?: string
  interests: string[]
  constraints: string[]
  notes?: string
  street_address?: string
  city?: string
  state_province?: string
  postal_code?: string
  country?: string
  address_validation_status?: 'validated' | 'unvalidated' | 'failed'
  created_at: string
  updated_at: string
  upcoming_occasions_count?: number
  occasions?: Occasion[]
  past_gifts?: GiftIdea[]
}

interface TooltipData {
  recipient: RecipientDetail
  x: number
  y: number
}

export function NetworkGraph({ recipients, activeRecipientId, onNodeClick, isTyping = false }: NetworkGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)
  const [tooltip, setTooltip] = useState<TooltipData | null>(null)
  const [recipientDetails, setRecipientDetails] = useState<Map<string, RecipientDetail>>(new Map())
  const animationFrameRef = useRef<number | null>(null)
  const [selectedRecipient, setSelectedRecipient] = useState<RecipientDetail | null>(null)
  // Responsive: check on mount and resize - declare early so it can be used in useEffect
  const [isMounted, setIsMounted] = useState(false)

  // Set mounted state after component mounts
  useEffect(() => {
    setIsMounted(true)
  }, [])

  // Fetch recipient details for tooltip
  const fetchRecipientDetails = async (recipientId: string) => {
    if (recipientDetails.has(recipientId)) {
      return recipientDetails.get(recipientId)!
    }

    try {
      const response = await apiClient.get<RecipientDetail>(`/api/recipients/${recipientId}`)
      const details = response.data
      setRecipientDetails(prev => new Map(prev).set(recipientId, details))
      return details
    } catch (error) {
      console.error('Failed to fetch recipient details:', error)
      return null
    }
  }

  // Check if occasion is within 30 days
  const isOccasionWithin30Days = (occasion: Occasion): boolean => {
    if (!occasion.date) return false
    const occasionDate = new Date(occasion.date)
    const today = new Date()
    const diffTime = occasionDate.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays >= 0 && diffDays <= 30
  }

  // Get next occasion text
  const getNextOccasionText = (occasions: Occasion[] | undefined): string | null => {
    if (!occasions || occasions.length === 0) return null
    
    const today = new Date()
    const upcoming = occasions
      .filter(o => o.date && new Date(o.date) >= today && o.status !== 'done')
      .sort((a, b) => {
        const dateA = a.date ? new Date(a.date).getTime() : Infinity
        const dateB = b.date ? new Date(b.date).getTime() : Infinity
        return dateA - dateB
      })
    
    if (upcoming.length === 0) return null
    
    const next = upcoming[0]
    const occasionDate = new Date(next.date!)
    const diffTime = occasionDate.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return `${next.name} today`
    if (diffDays === 1) return `${next.name} tomorrow`
    return `${next.name} in ${diffDays} days`
  }

  // Get last gift text
  const getLastGiftText = (gifts: GiftIdea[] | undefined): string | null => {
    if (!gifts || gifts.length === 0) return null
    const lastGift = gifts[0]
    return `Last gift: ${lastGift.title}`
  }

  // Track when refs are attached
  const [refsReady, setRefsReady] = useState(false)
  
  // Check if refs are ready
  useEffect(() => {
    if (svgRef.current && containerRef.current && isMounted) {
      setRefsReady(true)
    } else {
      setRefsReady(false)
    }
  }, [isMounted, recipients]) // Re-check when mounted or recipients change

  useEffect(() => {
    // Only run on client side and after component is mounted and refs are ready
    if (typeof window === 'undefined' || !isMounted || !refsReady) return

    let retryTimer: NodeJS.Timeout | null = null
    let initialTimer: NodeJS.Timeout | null = null
    let retryCount = 0
    const MAX_RETRIES = 100 // Increased retries

    const updateGraph = () => {
      if (!svgRef.current || !containerRef.current || typeof window === 'undefined') {
        retryCount++
        if (retryCount > MAX_RETRIES) {
          console.error('NetworkGraph: Max retries reached. Refs not available:', {
            svgRef: !!svgRef.current,
            containerRef: !!containerRef.current,
            containerElement: containerRef.current,
            svgElement: svgRef.current,
            isMounted,
            windowAvailable: typeof window !== 'undefined'
          })
          return
        }
        // Retry after a short delay if refs aren't ready
        if (retryCount % 10 === 0) { // Log every 10th retry to reduce spam
          console.log(`NetworkGraph: Refs not ready, retrying... (${retryCount}/${MAX_RETRIES})`, {
            svgRef: !!svgRef.current,
            containerRef: !!containerRef.current,
            window: typeof window !== 'undefined',
            isMounted
          })
        }
        retryTimer = setTimeout(updateGraph, 100)
        return
      }
      
      // Reset retry count on success
      retryCount = 0

      const svg = d3.select(svgRef.current)
      svg.selectAll('*').remove()

      // Get container dimensions - use actual container size
      const container = containerRef.current
      const width = container.clientWidth || window.innerWidth || 800
      const height = container.clientHeight || (window.innerHeight - 64) || 600
      
      console.log('NetworkGraph: Rendering graph', {
        width,
        height,
        recipientsCount: recipients.length,
        containerWidth: container.clientWidth,
        containerHeight: container.clientHeight
      })
      
      // Set SVG dimensions - use 100% to fill container, viewBox for scaling
      svg.attr('width', '100%')
        .attr('height', '100%')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')
        .style('background', 'transparent') // Ensure background is transparent

      // Add SVG filters for shadow and glow
      const defs = svg.append('defs')
      
      // Shadow filter
      const shadowFilter = defs.append('filter')
        .attr('id', 'node-shadow')
        .attr('x', '-50%')
        .attr('y', '-50%')
        .attr('width', '200%')
        .attr('height', '200%')
      
      shadowFilter.append('feGaussianBlur')
        .attr('in', 'SourceAlpha')
        .attr('stdDeviation', 3)
        .attr('result', 'blur')
      
      shadowFilter.append('feOffset')
        .attr('in', 'blur')
        .attr('dx', 0)
        .attr('dy', 4)
        .attr('result', 'offsetBlur')
      
      const feComponentTransfer = shadowFilter.append('feComponentTransfer')
        .attr('in', 'offsetBlur')
        .attr('result', 'shadow')
      
      feComponentTransfer.append('feFuncA')
        .attr('type', 'linear')
        .attr('slope', 0.3)
      
      shadowFilter.append('feMerge')
        .append('feMergeNode')
        .attr('in', 'shadow')
        .append('feMergeNode')
        .attr('in', 'SourceGraphic')

      // Glow filter for active nodes
      const glowFilter = defs.append('filter')
        .attr('id', 'node-glow')
        .attr('x', '-100%')
        .attr('y', '-100%')
        .attr('width', '300%')
        .attr('height', '300%')
      
      glowFilter.append('feGaussianBlur')
        .attr('stdDeviation', 4)
        .attr('result', 'coloredBlur')
      
      const feMergeGlow = glowFilter.append('feMerge')
      feMergeGlow.append('feMergeNode').attr('in', 'coloredBlur')
      feMergeGlow.append('feMergeNode').attr('in', 'SourceGraphic')

      // Handle empty state - show placeholder message
      if (recipients.length === 0) {
        console.log('NetworkGraph: No recipients, showing empty state', { width, height })
        // Add a subtle background circle to make it more visible
        svg.append('circle')
          .attr('cx', width / 2)
          .attr('cy', height / 2)
          .attr('r', 100)
          .attr('fill', 'none')
          .attr('stroke', '#E2E8F0')
          .attr('stroke-width', 2)
          .attr('stroke-dasharray', '5,5')
          .style('opacity', 0.3)
        
        svg.append('text')
          .attr('x', width / 2)
          .attr('y', height / 2 - 30)
          .attr('text-anchor', 'middle')
          .attr('font-size', '28px')
          .attr('font-weight', '700')
          .attr('fill', '#64748B')
          .style('opacity', 0.8)
          .text('Your network will appear here')
        
        svg.append('text')
          .attr('x', width / 2)
          .attr('y', height / 2 + 20)
          .attr('text-anchor', 'middle')
          .attr('font-size', '18px')
          .attr('fill', '#94A3B8')
          .style('opacity', 0.7)
          .text('Try: "My mom loves gardening"')
        return
      }

      console.log('NetworkGraph: Rendering', recipients.length, 'recipients', recipients)

      // Create nodes with recipient data
      const nodes = recipients.map((r) => ({
        id: r.id,
        name: r.name,
        type: 'recipient',
        recipient: r,
        fx: undefined as number | undefined,
        fy: undefined as number | undefined,
        vx: 0,
        vy: 0
      }))

      // Create links from relationships
      const links: Array<{ source: string; target: string; relationship: string }> = []
      recipients.forEach((recipient) => {
        if (recipient.relationships && recipient.relationships.length > 0) {
          recipient.relationships.forEach((rel) => {
            // Check if target recipient exists in nodes
            const targetExists = nodes.some((n) => n.id === rel.to_recipient_id)
            if (targetExists) {
              links.push({
                source: recipient.id,
                target: rel.to_recipient_id,
                relationship: rel.relationship_type
              })
            }
          })
        }
      })

      // Create force simulation
      const simulation = d3
        .forceSimulation(nodes as any)
        .force('charge', d3.forceManyBody().strength(-200))
        .force('center', d3.forceCenter(width / 2, height / 2).strength(0.1))
        .force('collision', d3.forceCollide().radius(70)) // Increased for larger nodes
        .force('x', d3.forceX(width / 2).strength(0.05))
        .force('y', d3.forceY(height / 2).strength(0.05))
        .force('link', d3.forceLink(links).id((d: any) => d.id).distance(150).strength(0.5))

      // Draw links (edges) for relationships
      const linkGroup = svg.append('g').attr('class', 'links')
      const linkElements = linkGroup
        .selectAll('line')
        .data(links)
        .enter()
        .append('line')
        .attr('stroke', '#94A3B8')
        .attr('stroke-width', 2)
        .attr('stroke-opacity', 0.6)
        .attr('marker-end', 'url(#arrowhead)')

      // Add arrowhead marker for directed edges
      const marker = defs.append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 55) // Position arrow at edge of node
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
      
      marker.append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#94A3B8')

      // Create node groups (for badge positioning)
      const nodeGroups = svg
        .append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(nodes.filter((d: any) => d.type !== 'user'))
        .enter()
        .append('g')
        .attr('class', 'node-group')
        .style('cursor', 'pointer')
        .style('transform', 'translateZ(0)') // GPU acceleration
        .style('pointer-events', 'all') // Enable pointer events for nodes

      // Draw circles with shadow
      const nodeCircles = nodeGroups
        .append('circle')
        .attr('r', 50) // Increased size for visibility
        .attr('fill', (d: any) => {
          if (activeRecipientId && d.id === activeRecipientId) {
            return '#FF6B6B'
          }
          const recipient = recipients.find(r => r.id === d.id)
          if (recipient?.relationship) {
            const rel = recipient.relationship.toLowerCase()
            if (['mom', 'dad', 'sister', 'brother', 'sibling'].includes(rel)) {
              return '#FF6B6B'
            } else if (['wife', 'husband', 'partner', 'spouse'].includes(rel)) {
              return '#FFA07A'
            } else if (['friend', 'buddy', 'pal'].includes(rel)) {
              return '#14B8A6'
            }
          }
          return '#CBD5E1'
        })
        .attr('stroke', '#fff')
        .attr('stroke-width', 4) // Increased stroke width
        .attr('filter', (d: any) => {
          if (activeRecipientId && d.id === activeRecipientId) {
            return 'url(#node-glow)'
          }
          return 'url(#node-shadow)'
        })
        .style('opacity', (d: any) => {
          if (isTyping) return 0.3
          return (activeRecipientId && d.id === activeRecipientId) ? 1 : 0.9 // Increased opacity
        })
        .style('transition', 'opacity 0.3s ease')
        .on('click', async (event, d: any) => {
          event.stopPropagation()
          if (d.type === 'recipient') {
            const recipient = recipients.find(r => r.id === d.id)
            if (recipient) {
              // If onNodeClick is provided (dashboard), use it
              if (onNodeClick) {
                onNodeClick(recipient)
              } else {
                // Otherwise, show modal (network page)
                const details = await fetchRecipientDetails(d.id)
                if (details) {
                  setSelectedRecipient(details)
                }
              }
            }
          }
        })
        .on('mouseenter', async function(event, d: any) {
          d3.select(this)
            .style('opacity', 1)
            .attr('r', 55) // Increased hover size
        
          // Fetch and show tooltip
          const details = await fetchRecipientDetails(d.id)
          if (details) {
            setTooltip({
              recipient: details,
              x: event.pageX,
              y: event.pageY
            })
          }
        })
        .on('mouseleave', function(event, d: any) {
          d3.select(this)
            .style('opacity', (activeRecipientId && d.id === activeRecipientId) ? 1 : 0.9)
            .attr('r', 50) // Back to normal size
        
          setTooltip(null)
        })

      // Add drag functionality to node groups
      nodeGroups.call(
        d3.drag<SVGGElement, any>()
          .on('start', function(event, d: any) {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
          })
          .on('drag', function(event, d: any) {
            d.fx = event.x
            d.fy = event.y
          })
          .on('end', function(event, d: any) {
            if (!event.active) simulation.alphaTarget(0)
            // Spring back: release fixed position after a delay
            setTimeout(() => {
              d.fx = undefined
              d.fy = undefined
              simulation.alpha(0.3).restart()
            }, 100)
          }) as any
      )

      // Add red badge for occasions within 30 days
      nodeGroups
        .filter((d: any) => {
          const recipient = recipients.find(r => r.id === d.id)
          const details = recipientDetails.get(d.id)
          if (details?.occasions) {
            return details.occasions.some(o => isOccasionWithin30Days(o))
          }
          // Fallback: show badge if upcoming_occasions_count > 0
          return (recipient as any)?.upcoming_occasions_count > 0
        })
        .append('circle')
        .attr('r', 6)
        .attr('fill', '#EF4444')
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .attr('cx', 28)
        .attr('cy', -28)
        .style('pointer-events', 'none')

      // Add labels with initials
      const labels = nodeGroups
        .append('text')
        .text((d: any) => {
          const name = d.name || ''
          return name.substring(0, 2).toUpperCase()
        })
        .attr('font-size', '14px')
        .attr('font-weight', '600')
        .attr('fill', '#fff')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .style('pointer-events', 'none')

      // Add pulsing animation for active nodes
      if (activeRecipientId) {
        const activeNode = nodeGroups.filter((d: any) => d.id === activeRecipientId)
        const pulseRing = activeNode
          .append('circle')
          .attr('r', 40)
          .attr('fill', 'none')
          .attr('stroke', '#FF6B6B')
          .attr('stroke-width', 2)
          .attr('opacity', 0.6)
          .style('pointer-events', 'none')
        
        // Animate pulse ring
        const animatePulse = () => {
          pulseRing
            .transition()
            .duration(2000)
            .ease(d3.easeSinInOut)
            .attr('r', 50)
            .attr('opacity', 0)
            .transition()
            .duration(0)
            .attr('r', 40)
            .attr('opacity', 0.6)
            .on('end', animatePulse)
        }
        animatePulse()
      }

      // Update positions on simulation tick with requestAnimationFrame
      simulation.on('tick', () => {
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
        }
        
        animationFrameRef.current = requestAnimationFrame(() => {
          // Update link positions
          linkElements
            .attr('x1', (d: any) => (d.source as any).x || 0)
            .attr('y1', (d: any) => (d.source as any).y || 0)
            .attr('x2', (d: any) => (d.target as any).x || 0)
            .attr('y2', (d: any) => (d.target as any).y || 0)
          
          // Update node positions
          nodeGroups.attr('transform', (d: any) => {
            if (d.x === undefined || d.y === undefined) return 'translate(0, 0)'
            return `translate(${d.x}, ${d.y})`
          })
        })
      })

      // Run simulation for initial positioning
      simulation.stop()
      for (let i = 0; i < 100; i++) {
        simulation.tick()
      }
      
      // Update link positions after initial simulation
      linkElements
        .attr('x1', (d: any) => (d.source as any).x || 0)
        .attr('y1', (d: any) => (d.source as any).y || 0)
        .attr('x2', (d: any) => (d.target as any).x || 0)
        .attr('y2', (d: any) => (d.target as any).y || 0)
      
      // Update positions after initial simulation
      nodeGroups.attr('transform', (d: any) => {
        if (d.x === undefined || d.y === undefined || isNaN(d.x) || isNaN(d.y)) {
          // If node hasn't been positioned, place it at center initially
          console.log('Node not positioned, placing at center', d)
          return `translate(${width / 2}, ${height / 2})`
        }
        return `translate(${d.x}, ${d.y})`
      })
      
      console.log('NetworkGraph: Nodes positioned', nodes.map((n: any) => ({ id: n.id, x: n.x, y: n.y })))
      
      // Restart simulation with lower alpha for subtle movement
      simulation.alpha(0.1).restart()

      // Pulse animation is handled via CSS
    }

    // Initial render with a small delay to ensure DOM is ready
    initialTimer = setTimeout(() => {
      updateGraph()
    }, 100)

    // Handle window resize
    const handleResize = () => {
      updateGraph()
    }
    
    // Watch for container size changes
    let resizeObserver: ResizeObserver | null = null
    if (typeof window !== 'undefined' && containerRef.current) {
      window.addEventListener('resize', handleResize)
      
      // Use ResizeObserver to watch container size changes
      resizeObserver = new ResizeObserver(() => {
        updateGraph()
      })
      resizeObserver.observe(containerRef.current)
    }

    return () => {
      if (retryTimer) {
        clearTimeout(retryTimer)
      }
      if (initialTimer) {
        clearTimeout(initialTimer)
      }
      if (typeof window !== 'undefined') {
        window.removeEventListener('resize', handleResize)
      }
      if (resizeObserver && containerRef.current) {
        resizeObserver.unobserve(containerRef.current)
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }

    // Initial render with a small delay to ensure DOM is ready
    const timer = setTimeout(() => {
      updateGraph()
    }, 50)

    return () => {
      clearTimeout(timer)
      if (typeof window !== 'undefined') {
        window.removeEventListener('resize', handleResize)
      }
      if (resizeObserver && containerRef.current) {
        resizeObserver.unobserve(containerRef.current)
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [recipients, activeRecipientId, onNodeClick, isTyping, recipientDetails, isMounted, refsReady])

  // Update tooltip position on mouse move
  useEffect(() => {
    if (typeof window === 'undefined') return
    
    const handleMouseMove = (e: MouseEvent) => {
      if (tooltip) {
        setTooltip({
          ...tooltip,
          x: e.pageX,
          y: e.pageY
        })
      }
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [tooltip])

  const nextOccasion = tooltip ? getNextOccasionText(tooltip.recipient.occasions) : null
  const lastGift = tooltip ? getLastGiftText(tooltip.recipient.past_gifts) : null

  return (
    <>
      {/* Always render the container and SVG so refs can attach */}
      <div 
        ref={(el) => {
          // Use callback ref to ensure ref is set
          if (el) {
            (containerRef as React.MutableRefObject<HTMLDivElement | null>).current = el
            // Trigger re-check of refs
            if (svgRef.current && isMounted) {
              setRefsReady(true)
            }
          }
        }}
        className="w-full h-full"
        style={{ 
          position: 'relative',
          width: '100%',
          height: '100%',
          minHeight: '400px',
          zIndex: 0,
          backgroundColor: 'transparent'
        }}
      >
        <svg
          ref={(el) => {
            // Use callback ref to ensure ref is set
            if (el) {
              (svgRef as React.MutableRefObject<SVGSVGElement | null>).current = el
              // Trigger re-check of refs
              if (containerRef.current && isMounted) {
                setRefsReady(true)
              }
            }
          }}
          className="transition-opacity duration-300"
          style={{ 
            width: '100%',
            height: '100%',
            minHeight: '400px',
            opacity: isMounted ? (isTyping ? 0.3 : 1) : 0, // Hide until mounted
            display: 'block',
            pointerEvents: recipients.length > 0 ? 'auto' : 'none',
            zIndex: 0,
            backgroundColor: 'transparent'
          }}
        />
        {!isMounted && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-gray-500">Loading graph...</div>
          </div>
        )}
      </div>
      
      {/* Tooltip */}
      {tooltip && (
        <div
          ref={tooltipRef}
          style={{
            position: 'fixed',
            left: `${tooltip.x + 10}px`,
            top: `${tooltip.y + 10}px`,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            padding: '12px 16px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            pointerEvents: 'none',
            zIndex: 1000,
            minWidth: '200px',
            fontSize: '14px',
            color: '#2D3748',
            transform: 'translateZ(0)'
          }}
        >
          <div style={{ fontWeight: '600', marginBottom: '4px' }}>
            {tooltip.recipient.name}
          </div>
          {tooltip.recipient.relationship && (
            <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>
              {tooltip.recipient.relationship}
            </div>
          )}
          {nextOccasion && (
            <div style={{ fontSize: '12px', color: '#14B8A6', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #E2E8F0' }}>
              {nextOccasion}
            </div>
          )}
          {lastGift && (
            <div style={{ fontSize: '12px', color: '#718096', marginTop: '4px' }}>
              {lastGift}
            </div>
          )}
        </div>
      )}

      {/* Recipient Modal */}
      {selectedRecipient && (
        <RecipientModal
          recipient={selectedRecipient}
          occasions={selectedRecipient.occasions}
          pastGifts={selectedRecipient.past_gifts}
          onClose={() => setSelectedRecipient(null)}
        />
      )}
      
    </>
  )
}
