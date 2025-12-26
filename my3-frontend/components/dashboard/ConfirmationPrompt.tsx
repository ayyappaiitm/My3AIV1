'use client'

interface ConfirmationPromptProps {
  message: string
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmationPrompt({
  message,
  onConfirm,
  onCancel,
}: ConfirmationPromptProps) {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
      <p className="text-text mb-3">{message}</p>
      <div className="flex gap-2">
        <button
          onClick={onConfirm}
          className="px-4 py-2 bg-accent text-white rounded-lg hover:opacity-90 transition-opacity"
        >
          Confirm
        </button>
        <button
          onClick={onCancel}
          className="px-4 py-2 bg-gray-200 text-text rounded-lg hover:bg-gray-300 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}

