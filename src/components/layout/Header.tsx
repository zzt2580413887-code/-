'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Bell, User, ChevronDown, LogOut, Settings } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'
import { logout } from '@/lib/api'

export default function Header() {
  const { user, isAuthenticated, isAdmin: userIsAdmin } = useAuth()
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleLogout = async () => {
    await logout()
  }

  return (
    <motion.div
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="bg-white border-b border-gray-100 px-4 py-3 flex items-center justify-between"
    >
      <div className="flex items-center space-x-4">
        <h1 className="text-xl font-medium bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-800 font-['Noto_Sans_SC']">
          城市治理综合研究平台
        </h1>
        <span className="text-sm text-gray-500 hidden sm:inline-block">
          全方位赋能城市治理研究工作
        </span>
      </div>

      <div className="flex items-center space-x-4">
        {isAuthenticated && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 rounded-lg hover:bg-gray-50 relative"
          >
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </motion.button>
        )}

        {isAuthenticated && user ? (
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 hover:bg-gray-50 p-2 rounded-lg transition-colors"
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                userIsAdmin
                  ? 'bg-gradient-to-r from-purple-500 to-purple-600'
                  : 'bg-gradient-to-r from-blue-500 to-blue-600'
              }`}>
                <span className="text-white font-medium">
                  {user.username.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex flex-col items-start">
                <span className="text-sm text-gray-700">{user.username}</span>
                <span className={`text-xs ${
                  userIsAdmin ? 'text-purple-600' : 'text-blue-600'
                }`}>
                  {userIsAdmin ? '管理员' : '用户'}
                </span>
              </div>
              <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${
                showUserMenu ? 'rotate-180' : ''
              }`} />
            </button>

            <AnimatePresence>
              {showUserMenu && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                  className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-2 z-50"
                  onMouseLeave={() => setShowUserMenu(false)}
                >
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">{user.username}</p>
                    <p className="text-xs text-gray-500">{user.role}</p>
                  </div>

                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>退出登录</span>
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ) : (
          <Link
            href="/login"
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all"
          >
            <User className="w-4 h-4" />
            <span className="text-sm font-medium">登录</span>
          </Link>
        )}
      </div>
    </motion.div>
  )
}
