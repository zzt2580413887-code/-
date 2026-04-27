import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/Providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: '城市治理研究综合平台',
  description: '城市治理研究综合平台',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body className={`${inter.className} bg-slate-50`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
