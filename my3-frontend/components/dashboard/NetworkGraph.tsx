'use client'

import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

interface Recipient {
  id: string
  name: string
  relationship?: string
}

interface NetworkGraphProps {
  recipients: Recipient[]
}

export function NetworkGraph({ recipients }: NetworkGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || recipients.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = svgRef.current.clientWidth || 800
    const height = svgRef.current.clientHeight || 600

    // Create center node (user)
    const nodes = [
      { id: 'user', name: 'You', type: 'user' },
      ...recipients.map((r) => ({ id: r.id, name: r.name, type: 'recipient' })),
    ]

    // Create links from user to recipients
    const links = recipients.map((r) => ({
      source: 'user',
      target: r.id,
    }))

    // Create force simulation
    const simulation = d3
      .forceSimulation(nodes as any)
      .force(
        'link',
        d3.forceLink(links).id((d: any) => d.id).distance(150)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))

    // Draw links
    const link = svg
      .append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#E2E8F0')
      .attr('stroke-width', 2)

    // Draw nodes
    const node = svg
      .append('g')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', (d: any) => (d.type === 'user' ? 20 : 15))
      .attr('fill', (d: any) => (d.type === 'user' ? '#FF6B6B' : '#14B8A6'))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')

    // Add labels
    const labels = svg
      .append('g')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .text((d: any) => d.name)
      .attr('font-size', '12px')
      .attr('fill', '#2D3748')
      .attr('text-anchor', 'middle')
      .attr('dy', (d: any) => (d.type === 'user' ? 35 : 30))

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y)

      labels.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y)
    })
  }, [recipients])

  return (
    <svg
      ref={svgRef}
      className="w-full h-full"
      style={{ minHeight: '100vh' }}
    />
  )
}

