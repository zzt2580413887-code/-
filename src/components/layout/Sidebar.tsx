'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  MessageSquare,
  FileText,
  ClipboardList,
  BarChart2,
  Clock,
  Star,
  ChevronRight,
  Gauge
} from 'lucide-react'

const menuItems = [
  {
    name: '智能AI助手',
    icon: MessageSquare,
    href: '/chat',
    gradient: 'from-blue-500 to-blue-600'
  },
  {
    name: '知识库管理',
    icon: FileText,
    href: '/documents',
    gradient: 'from-indigo-500 to-indigo-600'
  },
  {
    name: '审批流程（旧功能）',
    icon: ClipboardList,
    href: '/approval',
    gradient: 'from-violet-500 to-violet-600'
  },
  {
    name: '业务数据（旧功能）',
    icon: BarChart2,
    href: '/analytics',
    gradient: 'from-blue-600 to-indigo-600'
  },
  {
    name: '模型评测',
    icon: Gauge,
    href: '/evaluation',
    gradient: 'from-cyan-500 to-blue-500'
  },
  {
    name: '操作历史（旧功能）',
    icon: Clock,
    href: '/history',
    gradient: 'from-violet-500 to-purple-600'
  },
  {
    name: '我的收藏（旧功能）',
    icon: Star,
    href: '/favorites',
    gradient: 'from-blue-500 to-violet-600'
  }
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="w-64 bg-white border-r border-gray-100 py-6 flex flex-col">
      {/* Logo */}
      <div className="px-6 mb-8">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
          <span className="text-2xl font-bold text-white">hi</span>
        </div>
      </div>

      {/* 菜单项 */}
      <nav className="flex-1 px-3">
        {menuItems.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link key={item.href} href={item.href}>
              <motion.div
                whileHover={{ x: 4 }}
                className={`
                  flex items-center space-x-3 px-3 py-2 rounded-lg mb-1 cursor-pointer
                  ${isActive 
                    ? `bg-gradient-to-r ${item.gradient} text-white` 
                    : 'text-gray-600 hover:bg-gray-50'
                  }
                `}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-500'}`} />
                <span className="flex-1">{item.name}</span>
                {isActive && <ChevronRight className="w-4 h-4" />}
              </motion.div>
            </Link>
          )
        })}
      </nav>

      {/* 版本信息 */}
      <div className="px-6 py-4">
        <div className="text-xs text-gray-500">
          <p>城市治理综合研究平台</p>
          <p className="mt-1">©2026 All Rights Reserved</p>
        </div>
      </div>
    </div>
  )
}
