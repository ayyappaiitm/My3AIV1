'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ExternalLink, Heart, ShoppingBag, MoreVertical } from 'lucide-react'
import Image from 'next/image'
import { GiftIdea } from '@/lib/types'
import { extractOgImage, getUnsplashImageUrl } from '@/lib/utils/imageExtractor'

interface GiftCardProps {
  gift: GiftIdea
  onShortlist?: (giftId: string) => void
  onCategoryLike?: (category: string) => void
  recipientName?: string
}

// Get emoji for category (fallback)
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
  if (categoryLower.includes('experience')) return '🎫'
  return '🎁'
}

export function GiftCard({ gift, onShortlist, onCategoryLike, recipientName }: GiftCardProps) {
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [imageError, setImageError] = useState(false)
  const [isLoadingImage, setIsLoadingImage] = useState(true)
  const [isExpanded, setIsExpanded] = useState(false)
  const [categoryLiked, setCategoryLiked] = useState(false)
  const categoryEmoji = getCategoryEmoji(gift.category)
  const isShortlisted = gift.is_shortlisted === 'true' || gift.is_shortlisted === '1'
  
  // Check if rationale needs expansion (more than 2 lines)
  const displayReason = gift.personalized_reason || 
    (recipientName ? `Perfect for ${recipientName}` : 'A thoughtful gift choice')
  const needsExpansion = displayReason.length > 100 // Approximate 2-line threshold

  // Image loading strategy
  useEffect(() => {
    const loadImage = async () => {
      setIsLoadingImage(true)
      setImageError(false)

      // Strategy 1: Use image_url from backend (LLM-provided)
      if (gift.image_url) {
        setImageUrl(gift.image_url)
        setIsLoadingImage(false)
        return
      }

      // Strategy 2: Extract OG image from URL (client-side)
      if (gift.url) {
        const extracted = await extractOgImage(gift.url)
        if (extracted) {
          setImageUrl(extracted)
          setIsLoadingImage(false)
          return
        }
      }

      // Strategy 3: Use Unsplash based on category/title
      if (gift.category || gift.title) {
        const unsplashUrl = getUnsplashImageUrl(gift.category || '', gift.title)
        setImageUrl(unsplashUrl)
        setIsLoadingImage(false)
        return
      }

      // Strategy 4: No image available
      setIsLoadingImage(false)
      setImageError(true)
    }

    loadImage()
  }, [gift.image_url, gift.url, gift.category, gift.title])

  const handleImageError = () => {
    // If image fails, try Unsplash fallback
    if (imageUrl && !imageUrl.includes('unsplash.com')) {
      const unsplashUrl = getUnsplashImageUrl(gift.category || '', gift.title)
      setImageUrl(unsplashUrl)
    } else {
      setImageError(true)
      setIsLoadingImage(false)
    }
  }

  // Generate search URLs for Google/Amazon
  const getSearchUrl = (platform: 'google' | 'amazon'): string => {
    const searchQuery = encodeURIComponent(`${gift.title} ${gift.category || 'gift'}`)
    if (platform === 'google') {
      return `https://www.google.com/search?q=${searchQuery}&tbm=shop`
    } else {
      return `https://www.amazon.com/s?k=${searchQuery}`
    }
  }

  const handleCategoryLike = () => {
    if (gift.category && onCategoryLike) {
      setCategoryLiked(!categoryLiked)
      onCategoryLike(gift.category)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-xl hover:scale-[1.02] transition-all duration-200 flex flex-col w-full h-full"
      style={{
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
      }}
    >
      {/* Category at Top with Heart Icon - Above Image */}
      {gift.category && (
        <div className="flex items-center justify-between px-4 pt-3 pb-2">
          <span className="text-xs px-3 py-1.5 bg-gray-100 text-gray-700 rounded-full font-medium capitalize">
            {gift.category}
          </span>
          <button
            onClick={handleCategoryLike}
            className={`p-1.5 rounded-full transition-colors ${
              categoryLiked
                ? 'text-[#FF6B6B] bg-red-50'
                : 'text-gray-400 hover:text-[#FF6B6B] hover:bg-gray-50'
            }`}
            aria-label={categoryLiked ? 'Unlike category' : 'Like category'}
          >
            <Heart size={16} fill={categoryLiked ? 'currentColor' : 'none'} />
          </button>
        </div>
      )}

      {/* Image Section - 16:9 aspect ratio */}
      <div className="relative w-full h-48 bg-gradient-to-br from-[#FF6B6B]/10 to-[#FFA07A]/10 overflow-hidden">
        {/* Shortlist button - Top right overlay */}
        {onShortlist && (
          <button
            onClick={() => onShortlist(gift.id)}
            className={`absolute top-2 right-2 z-10 p-2 rounded-full transition-colors ${
              isShortlisted
                ? 'bg-[#FF6B6B] text-white shadow-lg'
                : 'bg-white/90 text-gray-400 hover:bg-white hover:text-[#FF6B6B]'
            }`}
            aria-label={isShortlisted ? 'Remove from shortlist' : 'Add to shortlist'}
          >
            <Heart size={18} fill={isShortlisted ? 'currentColor' : 'none'} />
          </button>
        )}

        {/* Product Image or Fallback */}
        {isLoadingImage && !imageError && (
          <div className="absolute inset-0 bg-gray-200 animate-pulse" />
        )}

        {imageUrl && !imageError ? (
          <Image
            src={imageUrl}
            alt={gift.title}
            fill
            className="object-cover"
            onError={handleImageError}
            onLoad={() => setIsLoadingImage(false)}
            unoptimized
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-6xl" role="img" aria-label={gift.category || 'gift'}>
              {categoryEmoji}
            </span>
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="flex-1 flex flex-col p-4">
        {/* Title */}
        <h4 className="font-bold text-lg text-gray-800 line-clamp-2 mb-2">
          {gift.title}
        </h4>

        {/* Price */}
        {gift.price && (
          <div className="mb-3">
            <span className="text-xl font-bold bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] bg-clip-text text-transparent">
              {gift.price}
            </span>
          </div>
        )}

        {/* Personalized Reason - Expandable */}
        <div className="mb-3">
          <div className="flex items-start gap-2">
            <p className={`text-sm text-gray-600 italic leading-relaxed flex-1 ${
              isExpanded ? '' : 'line-clamp-2'
            }`}>
              {displayReason}
            </p>
            {needsExpansion && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 transition-colors"
                aria-label={isExpanded ? 'Show less' : 'Show more'}
              >
                <MoreVertical size={16} />
              </button>
            )}
          </div>
        </div>

        {/* Buy Now Button - Always visible */}
        <div className="mt-auto">
          {gift.url ? (
            <a
              href={gift.url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity shadow-md hover:shadow-lg"
            >
              <ShoppingBag size={18} />
              <span>Buy Now</span>
              <ExternalLink size={16} />
            </a>
          ) : (
            <div className="flex gap-2">
              <a
                href={getSearchUrl('google')}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity shadow-md hover:shadow-lg"
              >
                <ShoppingBag size={18} />
                <span>Buy Now</span>
                <ExternalLink size={16} />
              </a>
              <a
                href={getSearchUrl('amazon')}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-3 bg-[#FF9900] text-white rounded-lg hover:bg-[#FF8800] transition-colors shadow-md hover:shadow-lg"
                aria-label="Search on Amazon"
                title="Search on Amazon"
              >
                <span className="text-xs font-bold">A</span>
              </a>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

