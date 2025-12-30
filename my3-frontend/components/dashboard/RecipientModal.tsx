'use client'

import { useEffect } from 'react'
import { X } from 'lucide-react'
import { Recipient, Occasion, GiftIdea } from '@/lib/types'
import { motion, AnimatePresence } from 'framer-motion'

interface RecipientModalProps {
  recipient: Recipient | null
  occasions?: Occasion[]
  pastGifts?: GiftIdea[]
  onClose: () => void
}

export function RecipientModal({ recipient, occasions, pastGifts, onClose }: RecipientModalProps) {
  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [onClose])

  if (!recipient) return null

  // Get next occasion
  const getNextOccasion = (): Occasion | null => {
    if (!occasions || occasions.length === 0) return null
    
    const today = new Date()
    const upcoming = occasions
      .filter(o => o.date && new Date(o.date) >= today && o.status !== 'done')
      .sort((a, b) => {
        const dateA = a.date ? new Date(a.date).getTime() : Infinity
        const dateB = b.date ? new Date(b.date).getTime() : Infinity
        return dateA - dateB
      })
    
    return upcoming.length > 0 ? upcoming[0] : null
  }

  const nextOccasion = getNextOccasion()
  const occasionDate = nextOccasion?.date ? new Date(nextOccasion.date) : null
  const daysUntil = occasionDate ? Math.ceil((occasionDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)) : null

  // Get relationship color
  const getRelationshipColor = (relationship?: string): string => {
    if (!relationship) return '#CBD5E1'
    const rel = relationship.toLowerCase()
    if (['mom', 'dad', 'sister', 'brother', 'sibling'].includes(rel)) {
      return '#FF6B6B'
    } else if (['wife', 'husband', 'partner', 'spouse'].includes(rel)) {
      return '#FFA07A'
    } else if (['friend', 'buddy', 'pal'].includes(rel)) {
      return '#14B8A6'
    }
    return '#CBD5E1'
  }

  return (
    <AnimatePresence>
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto z-10"
        >
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-2xl">
            <div className="flex items-center space-x-3">
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold text-lg"
                style={{ backgroundColor: getRelationshipColor(recipient.relationship) }}
              >
                {recipient.name.substring(0, 2).toUpperCase()}
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">{recipient.name}</h2>
                {recipient.relationship && (
                  <p className="text-sm text-gray-500 capitalize">{recipient.relationship}</p>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 space-y-6">
            {/* Next Occasion */}
            {nextOccasion && (
              <div className="bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] text-white rounded-xl p-4">
                <div className="text-sm font-medium opacity-90 mb-1">Next Occasion</div>
                <div className="text-lg font-bold">{nextOccasion.name}</div>
                {daysUntil !== null && (
                  <div className="text-sm mt-1 opacity-90">
                    {daysUntil === 0 && 'Today'}
                    {daysUntil === 1 && 'Tomorrow'}
                    {daysUntil > 1 && `In ${daysUntil} days`}
                    {occasionDate && (
                      <span className="ml-2">
                        ({occasionDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })})
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Age Band */}
            {recipient.age_band && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Age Range</h3>
                <p className="text-gray-600">{recipient.age_band}</p>
              </div>
            )}

            {/* Interests */}
            {recipient.interests && recipient.interests.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Interests</h3>
                <div className="flex flex-wrap gap-2">
                  {recipient.interests.map((interest, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      {interest}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Constraints */}
            {recipient.constraints && recipient.constraints.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Preferences</h3>
                <div className="flex flex-wrap gap-2">
                  {recipient.constraints.map((constraint, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-amber-50 text-amber-700 rounded-full text-sm border border-amber-200"
                    >
                      {constraint}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Notes */}
            {recipient.notes && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Notes</h3>
                <p className="text-gray-600 text-sm">{recipient.notes}</p>
              </div>
            )}

            {/* Address */}
            {(recipient.street_address || recipient.city) && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-sm font-semibold text-gray-700">Address</h3>
                  {recipient.address_validation_status && (
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        recipient.address_validation_status === 'validated'
                          ? 'bg-green-100 text-green-700'
                          : recipient.address_validation_status === 'unvalidated'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {recipient.address_validation_status === 'validated' && '✓ Validated'}
                      {recipient.address_validation_status === 'unvalidated' && '⚠ Unvalidated'}
                      {recipient.address_validation_status === 'failed' && '✗ Failed'}
                    </span>
                  )}
                </div>
                <div className="text-gray-600 text-sm space-y-1">
                  {recipient.street_address && <p>{recipient.street_address}</p>}
                  <p>
                    {recipient.city}
                    {recipient.state_province && `, ${recipient.state_province}`}
                    {recipient.postal_code && ` ${recipient.postal_code}`}
                  </p>
                  {recipient.country && <p>{recipient.country}</p>}
                </div>
              </div>
            )}

            {/* Past Gifts */}
            {pastGifts && pastGifts.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Recent Gifts</h3>
                <div className="space-y-2">
                  {pastGifts.slice(0, 3).map((gift) => (
                    <div
                      key={gift.id}
                      className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                    >
                      <div className="font-medium text-gray-900">{gift.title}</div>
                      {gift.description && (
                        <div className="text-sm text-gray-600 mt-1">{gift.description}</div>
                      )}
                      {gift.price && (
                        <div className="text-sm text-[#FF6B6B] font-semibold mt-1">{gift.price}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {!nextOccasion && !recipient.age_band && 
             (!recipient.interests || recipient.interests.length === 0) &&
             (!recipient.constraints || recipient.constraints.length === 0) &&
             !recipient.notes &&
             !recipient.street_address && !recipient.city &&
             (!pastGifts || pastGifts.length === 0) && (
              <div className="text-center py-8 text-gray-500">
                <p className="text-sm">No additional information available</p>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}

