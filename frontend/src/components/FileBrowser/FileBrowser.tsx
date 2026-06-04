import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FiFolder, FiFile, FiChevronRight, FiChevronDown, FiRefreshCw } from 'react-icons/fi'
import { fileApi, FileInfo, FileBrowseResponse } from '@/services/fileApi'

interface FileBrowserProps {
  onSelectFile: (path: string) => void
  basePaths: string[]
  title: string
}

export default function FileBrowser({ onSelectFile, basePaths, title }: FileBrowserProps) {
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set())
  const [currentPath, setCurrentPath] = useState<string>('')

  // 浏览目录
  const { data: browseData, isLoading, refetch } = useQuery<FileBrowseResponse>({
    queryKey: ['browse', currentPath],
    queryFn: () => fileApi.browse(currentPath),
    enabled: currentPath !== '',
  })

  // 初始化：加载第一个基础路径
  useState(() => {
    if (basePaths.length > 0 && !currentPath) {
      setCurrentPath(basePaths[0])
    }
  })

  const toggleExpand = (path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }

  const handleItemClick = (item: FileInfo) => {
    if (item.type === 'directory') {
      setCurrentPath(item.path)
      toggleExpand(item.path)
    } else {
      onSelectFile(item.path)
    }
  }

  const handlePathSelect = (path: string) => {
    setCurrentPath(path)
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      {/* 标题 */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <button
          onClick={() => refetch()}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
          title="刷新"
        >
          <FiRefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* 基础路径选择 */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          选择根目录
        </label>
        <select
          value={currentPath}
          onChange={(e) => handlePathSelect(e.target.value)}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        >
          {basePaths.map((path) => (
            <option key={path} value={path}>
              {path}
            </option>
          ))}
        </select>
      </div>

      {/* 当前路径 */}
      <div className="mb-2 px-3 py-2 bg-gray-50 rounded text-sm text-gray-600">
        当前路径: {currentPath}
      </div>

      {/* 文件列表 */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">
            加载中...
          </div>
        ) : browseData && browseData.items.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {/* 返回上级 */}
            {browseData.parent && (
              <button
                onClick={() => handlePathSelect(browseData.parent!)}
                className="w-full px-4 py-3 flex items-center hover:bg-gray-50 text-sm text-gray-600"
              >
                <FiChevronRight className="w-4 h-4 mr-2 rotate-180" />
                返回上级
              </button>
            )}

            {/* 文件/文件夹列表 */}
            {browseData.items.map((item) => (
              <button
                key={item.path}
                onClick={() => handleItemClick(item)}
                className="w-full px-4 py-3 flex items-center hover:bg-gray-50"
              >
                {item.type === 'directory' ? (
                  <FiFolder className="w-5 h-5 mr-3 text-primary-600" />
                ) : (
                  <FiFile className="w-5 h-5 mr-3 text-gray-400" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {item.name}
                  </p>
                  {item.type === 'directory' && item.file_count !== undefined && (
                    <p className="text-xs text-gray-500">
                      {item.file_count} 个文件
                    </p>
                  )}
                  {item.type === 'file' && item.size !== undefined && (
                    <p className="text-xs text-gray-500">
                      {(item.size / 1024).toFixed(2)} KB
                    </p>
                  )}
                </div>
                {item.type === 'directory' && (
                  expandedPaths.has(item.path) ? (
                    <FiChevronDown className="w-4 h-4 text-gray-400" />
                  ) : (
                    <FiChevronRight className="w-4 h-4 text-gray-400" />
                  )
                )}
              </button>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-gray-500">
            当前目录为空
          </div>
        )}
      </div>
    </div>
  )
}