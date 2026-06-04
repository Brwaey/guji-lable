import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FiHome, FiFileText, FiEdit, FiBarChart2 } from 'react-icons/fi'

interface MainLayoutProps {
  children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  const location = useLocation()

  const navItems = [
    { path: '/', icon: FiHome, label: '首页' },
    { path: '/compare', icon: FiFileText, label: '文本对比' },
    { path: '/annotations', icon: FiEdit, label: '标注管理' },
    { path: '/stats', icon: FiBarChart2, label: '统计查看' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">
                古籍标注平台
              </h1>
            </div>

            {/* 导航 */}
            <nav className="flex space-x-8">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      isActive
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.label}
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* 页脚 */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            古籍标注平台 © 2026 | Powered by FastAPI & React
          </p>
        </div>
      </footer>
    </div>
  )
}