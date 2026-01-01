'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { User, Search, LogOut, Settings, Network } from 'lucide-react'
import { Logo } from '@/components/ui/Logo'

export function Header() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [showProfileMenu, setShowProfileMenu] = useState(false)

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return (
    <header className="relative z-20 w-full bg-white/80 backdrop-blur-sm border-b border-gray-200/50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Logo variant="header" />

          {/* Search (Optional - placeholder for future) */}
          <div className="hidden md:flex flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search chat history..."
                className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#FF6B6B]/20 focus:border-[#FF6B6B]"
                disabled
                suppressHydrationWarning
              />
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-4 mr-4">
            <Link
              href="/network"
              className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors text-sm font-medium text-gray-700"
              suppressHydrationWarning
            >
              <Network className="w-4 h-4" />
              <span>View Network</span>
            </Link>
          </div>

          {/* Profile Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
              suppressHydrationWarning
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-[#FF6B6B] to-[#FFA07A] flex items-center justify-center text-white font-semibold text-sm">
                {user?.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span className="hidden sm:block text-sm font-medium text-gray-700">
                {user?.name || 'User'}
              </span>
            </button>

            {/* Dropdown Menu */}
            {showProfileMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowProfileMenu(false)}
                />
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                  </div>
                  {/* View Network - visible on mobile, hidden on desktop (where it's in the main nav) */}
                  <Link
                    href="/network"
                    onClick={() => setShowProfileMenu(false)}
                    className="md:hidden w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    suppressHydrationWarning
                  >
                    <Network className="w-4 h-4 mr-2" />
                    View Network
                  </Link>
                  <button
                    onClick={() => {
                      setShowProfileMenu(false)
                      // Settings placeholder
                    }}
                    className="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Settings
                  </button>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}


