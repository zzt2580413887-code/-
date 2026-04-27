'use client'

import MainLayout from '@/components/layout/MainLayout'
import Image from 'next/image'
import { motion } from 'framer-motion'
import { ArrowRight, ChevronRight, Database, Layers, MessageCircle, Gauge } from 'lucide-react'

export default function Home() {
  return (
    <MainLayout>
      <div className="gradient-bg min-h-screen">
        <div className="max-w-7xl mx-auto px-4 py-12">
          {/* Hero Section */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="gradient-card rounded-2xl shadow-lg p-8 mb-12"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <motion.h1 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-5xl font-bold text-gray-900 mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-800"
                >
                  城市治理综合研究平台
                </motion.h1>
                <motion.p 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 }}
                  className="text-xl text-gray-600 mb-8 max-w-2xl leading-relaxed"
                >
                  一个兼具知识底蕴与智能交互能力的城市治理综合研究平台
                </motion.p>
              </div>
              <motion.div 
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="hidden lg:block"
              >
                {/* <Image
                  src="/logo.png"
                  alt="Logo"
                  width={300}
                  height={300}
                  className="object-contain"
                /> */}
              </motion.div>
            </div>
          </motion.div>

          {/* 系统核心模块 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              {
                title: "城市治理研究知识库",
                description: "整合政策法规、学术论文、典型案例等核心语料，通过科学的标签体系与云端存储，实现了城市治理知识的标准化采集与高效化管理。",
                icon: Database,
                iconBg: "bg-blue-50",
                iconColor: "text-blue-600",
                hoverIconBg: "group-hover:bg-blue-600",
                hoverIconColor: "group-hover:text-white"
              },
              {
                title: "城市治理研究大模型",
                description: "基于国产大模型基座，采用后训练技术（SFT & DPO），针对城市治理垂直领域进行深度微调，提升了专业回答的严谨性。",
                icon: Layers,
                iconBg: "bg-indigo-50",
                iconColor: "text-indigo-600",
                hoverIconBg: "group-hover:bg-indigo-600",
                hoverIconColor: "group-hover:text-white"
              },
              {
                title: "城市治理研究智能问答系统",
                description: "设计两个多智能体框架，分别支撑深度研究（面向复杂议题的系统性、结构化研究需求）与数据分析（面向数据的探索、分析与可视化需求）任务",
                icon: MessageCircle,
                iconBg: "bg-emerald-50",
                iconColor: "text-emerald-600",
                hoverIconBg: "group-hover:bg-emerald-600",
                hoverIconColor: "group-hover:text-white"
              },
              {
                title: "城市治理研究能力测评体系",
                description: "发布 UrbanGovEval 评测基准，通过\"模拟主观评审\"方案与多元指标体系，量化评估模型在政策解析、任务推演等真实治理任务中的表现。",
                icon: Gauge,
                iconBg: "bg-rose-50",
                iconColor: "text-rose-600",
                hoverIconBg: "group-hover:bg-rose-600",
                hoverIconColor: "group-hover:text-white"
              }
            ].map((card, index) => (
              <motion.div
                key={card.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 * (index + 1) }}
                className="bg-white p-10 rounded-3xl shadow-lg hover:shadow-xl transition-all duration-300 group"
              >
                <div className={`w-12 h-12 ${card.iconBg} ${card.iconColor} rounded-2xl flex items-center justify-center mb-6 ${card.hoverIconBg} ${card.hoverIconColor} transition-colors`}>
                  <card.icon className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-gray-800">
                  {card.title}
                </h3>
                <p className="text-gray-500 text-sm leading-relaxed">
                  {card.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
