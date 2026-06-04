import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { FiFolder, FiFileText, FiEdit, FiBarChart2, FiArrowRight } from 'react-icons/fi'
import { fileApi } from '@/services/fileApi'
import { annotationApi } from '@/services/annotationApi'

export default function HomePage() {
  // 获取基础路径
  const { data: basePaths } = useQuery({
    queryKey: ['basePaths'],
    queryFn: fileApi.getBasePaths,
  })

  // 获取标注统计
  const { data: stats } = useQuery({
    queryKey: ['annotationStats'],
    queryFn: () => annotationApi.getStats(),
  })

  return (
    <div className="space-y-8">
      {/* 欢迎卡片 */}
      <div className="bg-gradient-to-r from-primary-600 to-secondary-600 rounded-lg shadow-lg p-8 text-white">
        <h2 className="text-3xl font-bold mb-4">欢迎使用古籍标注平台</h2>
        <p className="text-lg opacity-90 mb-6">
          本平台用于古籍OCR结果的质量评估与标注，支持文件浏览、相似度计算、文本对比和标注管理。
        </p>
        <div className="flex space-x-4">
          <Link
            to="/compare"
            className="inline-flex items-center px-6 py-3 bg-white text-primary-700 rounded-lg font-medium hover:bg-gray-100 transition-colors"
          >
            开始对比
            <FiArrowRight className="ml-2" />
          </Link>
          <Link
            to="/annotations"
            className="inline-flex items-center px-6 py-3 bg-white/20 text-white rounded-lg font-medium hover:bg-white/30 transition-colors"
          >
            查看标注
            <FiArrowRight className="ml-2" />
          </Link>
        </div>
      </div>

      {/* 快速统计 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-primary-100 text-primary-600">
              <FiFolder className="w-6 h-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">OCR目录</p>
              <p className="text-2xl font-semibold text-gray-900">
                {basePaths?.ocr_paths?.length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100 text-green-600">
              <FiFileText className="w-6 h-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">参考文本</p>
              <p className="text-2xl font-semibold text-gray-900">
                {basePaths?.reference_path ? 1 : 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-yellow-100 text-yellow-600">
              <FiEdit className="w-6 h-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">总标注数</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats?.total_annotations || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-purple-100 text-purple-600">
              <FiBarChart2 className="w-6 h-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-500">平均确信度</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats?.avg_confidence ? `${(stats.avg_confidence * 100).toFixed(0)}%` : '0%'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 功能介绍 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-primary-600 mb-4">
            <FiFolder className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">文件浏览</h3>
          <p className="text-gray-600">
            浏览服务器上的古籍OCR文件和参考文本，支持目录树展示和文件搜索。
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-green-600 mb-4">
            <FiFileText className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">相似度计算</h3>
          <p className="text-gray-600">
            基于Embedding计算OCR文本与参考文本的相似度，自动对齐和分块展示。
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-yellow-600 mb-4">
            <FiEdit className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">标注管理</h3>
          <p className="text-gray-600">
            支持多种标注类型，标注结果持久化保存，支持导出和统计分析。
          </p>
        </div>
      </div>

      {/* 最近工作 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">快速开始</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <span className="text-2xl mr-4">1️⃣</span>
              <div>
                <p className="font-medium text-gray-900">选择文件</p>
                <p className="text-sm text-gray-500">从目录树中选择OCR文件和参考文本</p>
              </div>
            </div>
            <Link to="/compare" className="text-primary-600 hover:text-primary-700">
              <FiArrowRight className="w-5 h-5" />
            </Link>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <span className="text-2xl mr-4">2️⃣</span>
              <div>
                <p className="font-medium text-gray-900">计算相似度</p>
                <p className="text-sm text-gray-500">系统自动计算Embedding相似度并展示对比</p>
              </div>
            </div>
            <Link to="/compare" className="text-primary-600 hover:text-primary-700">
              <FiArrowRight className="w-5 h-5" />
            </Link>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <span className="text-2xl mr-4">3️⃣</span>
              <div>
                <p className="font-medium text-gray-900">标注错误</p>
                <p className="text-sm text-gray-500">标记识别错误区域，添加修正建议</p>
              </div>
            </div>
            <Link to="/annotations" className="text-primary-600 hover:text-primary-700">
              <FiArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}