'use client'

import { motion } from 'framer-motion'
import { ExternalLink, Heart } from 'lucide-react'
import { GiftIdea } from '@/lib/types'

interface GiftInlineCardProps {
  gift: GiftIdea
  compact?: boolean
  onShortlist?: (giftId: string) => void
}

// Get emoji for category
const getCategoryEmoji = (category?: string): string => {
  if (!category) return '🎁'
  
  const categoryLower = category.toLowerCase()
  if (categoryLower.includes('book') || categoryLower.includes('reading')) return '📚'
  if (categoryLower.includes('coffee') || categoryLower.includes('tea')) return '☕'
  if (categoryLower.includes('tech') || categoryLower.includes('electronic')) return '💻'
  if (categoryLower.includes('clothing') || categoryLower.includes('fashion')) return '👕'
  if (categoryLower.includes('jewelry')) return '💍'
  if (categoryLower.includes('art') || categoryLower.includes('craft')) return '🎨'
  if (categoryLower.includes('sport') || categoryLower.includes('fitness')) return '⚽'
  if (categoryLower.includes('music')) return '🎵'
  if (categoryLower.includes('game')) return '🎮'
  if (categoryLower.includes('beauty') || categoryLower.includes('cosmetic')) return '💄'
  if (categoryLower.includes('home') || categoryLower.includes('decor')) return '🏠'
  if (categoryLower.includes('food') || categoryLower.includes('gourmet')) return '🍰'
  return '🎁'
}

export function GiftInlineCard({ gift, compact = false, onShortlist }: GiftInlineCardProps) {
  const categoryEmoji = getCategoryEmoji(gift.category)
  const isShortlisted = gift.is_shortlisted === 'true' || gift.is_shortlisted === true

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`bg-white border border-gray-200 rounded-xl overflow-hidden
        ${compact ? 'h-20' : 'h-[100px]'}
        hover:shadow-lg hover:scale-[1.02] transition-all duration-200
        flex flex-row sm:flex-row flex-col sm:flex-row
        w-full`}
      style={{
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      }}
    >
      {/* Left side - Icon/Image */}
      <div className={`
        ${compact ? 'w-20 h-20' : 'w-[100px] h-[100px]'}
        flex-shrink-0 flex items-center justify-center
        bg-gradient-to-br from-[#FF6B6B]/10 to-[#FFA07A]/10
      `}>
        <span className="text-4xl" role="img" aria-label={gift.category || 'gift'}>
          {categoryEmoji}
        </span>
      </div>

      {/* Right side - Content */}
      <div className="flex-1 flex flex-col justify-between p-3 sm:p-4 min-w-0">
        {/* Top row - Title and Price */}
        <div className="flex items-start justify-between gap-2 mb-1">
          <h4 className="font-semibold text-base text-gray-800 line-clamp-1 flex-1">
            {gift.title}
          </h4>
          {gift.price && (
            <span className="text-base font-bold text-[#FF6B6B] whitespace-nowrap flex-shrink-0">
              {gift.price}
            </span>
          )}
        </div>

        {/* Description */}
        {gift.description && (
          <p className={`text-sm text-gray-600 line-clamp-2 mb-2 ${compact ? 'line-clamp-1' : ''}`}>
            {gift.description}
          </p>
        )}

        {/* Bottom row - Category and Actions */}
        <div className="flex items-center justify-between gap-2 mt-auto">
          {/* Category badge */}
          {gift.category && (
            <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full whitespace-nowrap">
              {gift.category}
            </span>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2 ml-auto">
            {/* Shortlist button (heart icon) */}
            {onShortlist && (
              <button
                onClick={() => onShortlist(gift.id)}
                className={`p-1.5 rounded-lg transition-colors ${
                  isShortlisted
                    ? 'bg-[#FF6B6B] text-white'
                    : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                }`}
                aria-label={isShortlisted ? 'Remove from shortlist' : 'Add to shortlist'}
              >
                <Heart size={16} fill={isShortlisted ? 'currentColor' : 'none'} />
              </button>
            )}

            {/* View & Buy button */}
            {gift.url && (
              <a
                href={gift.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] text-white text-sm font-medium rounded-lg hover:opacity-90 transition-opacity whitespace-nowrap"
              >
                <span>View & Buy</span>
                <ExternalLink size={14} />
              </a>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
