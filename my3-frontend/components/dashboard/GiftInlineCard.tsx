'use client'

interface GiftIdea {
  id: string
  title: string
  description?: string
  price?: string
  url?: string
}

interface GiftInlineCardProps {
  gift: GiftIdea
  onSelect?: (giftId: string) => void
}

export function GiftInlineCard({ gift, onSelect }: GiftInlineCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <h3 className="font-semibold text-text mb-1">{gift.title}</h3>
      {gift.description && (
        <p className="text-sm text-text-light mb-2">{gift.description}</p>
      )}
      <div className="flex items-center justify-between">
        {gift.price && (
          <span className="text-accent font-medium">{gift.price}</span>
        )}
        <div className="flex gap-2">
          {gift.url && (
            <a
              href={gift.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline"
            >
              View
            </a>
          )}
          {onSelect && (
            <button
              onClick={() => onSelect(gift.id)}
              className="text-sm bg-accent text-white px-3 py-1 rounded hover:opacity-90"
            >
              Select
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

