import { useState, useEffect } from 'react'
import { FiTrash2, FiDownload, FiFilter, FiSearch, FiCheck, FiX } from 'react-icons/fi'
import { annotationApi, Annotation } from '@/services/annotationApi'
import toast from 'react-hot-toast'

export default function AnnotationManagePage() {
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  
  // 筛选状态
  const [filterType, setFilterType] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [searchText, setSearchText] = useState('')
  
  // 分页
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 50

  // 加载批注列表
  useEffect(() => {
    loadAnnotations()
  }, [])

  const loadAnnotations = async () => {
    try {
      setLoading(true)
      const response = await annotationApi.list({ page: 1, page_size: 1000 })
      setAnnotations(response.annotations)
    } catch (error: any) {
      toast.error(`加载失败: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  // 筛选后的批注
  const filteredAnnotations = annotations.filter(ann => {
    if (filterType !== 'all' && ann.annotation_type !== filterType) return false
    if (filterStatus !== 'all' && ann.status !== filterStatus) return false
    if (searchText && !ann.original_text.includes(searchText) && !ann.note?.includes(searchText)) return false
    return true
  })

  // 分页后的批注
  const paginatedAnnotations = filteredAnnotations.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  const totalPages = Math.ceil(filteredAnnotations.length / pageSize)

  // 批量操作
  const handleSelectAll = () => {
    if (selectedIds.size === paginatedAnnotations.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(paginatedAnnotations.map(a => a.annotation_id)))
    }
  }

  const handleSelect = (id: string) => {
    const newSet = new Set(selectedIds)
    if (newSet.has(id)) {
      newSet.delete(id)
    } else {
      newSet.add(id)
    }
    setSelectedIds(newSet)
  }

  const handleBatchDelete = async () => {
    if (!confirm(`确定删除 ${selectedIds.size} 条批注吗？`)) return
    
    try {
      for (const id of selectedIds) {
        await annotationApi.delete(id)
      }
      toast.success(`成功删除 ${selectedIds.size} 条批注`)
      setSelectedIds(new Set())
      loadAnnotations()
    } catch (error: any) {
      toast.error(`删除失败: ${error.message}`)
    }
  }

  const handleBatchConfirm = async () => {
    try {
      for (const id of selectedIds) {
        await annotationApi.update(id, { status: 'confirmed' })
      }
      toast.success(`成功确认 ${selectedIds.size} 条批注`)
      setSelectedIds(new Set())
      loadAnnotations()
    } catch (error: any) {
      toast.error(`确认失败: ${error.message}`)
    }
  }

  const handleExport = async (format: string) => {
    try {
      const response = await annotationApi.export({
        format,
        scope: 'all',
      })
      
      // 下载文件
      const blob = new Blob([response], { type: 'application/octet-stream' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `annotations.${format}`
      a.click()
      URL.revokeObjectURL(url)
      
      toast.success('导出成功')
    } catch (error: any) {
      toast.error(`导出失败: ${error.message}`)
    }
  }

  const getTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      error_char: '🔴 识别错误',
      missing: '📝 缺失内容',
      extra: '➕ 多余内容',
      format: '⚠️ 格式错误',
      unclear: '🔍 模糊不清',
      other: '❓ 其他问题',
    }
    return types[type] || type
  }

  const getStatusLabel = (status: string) => {
    const statuses: Record<string, { label: string; color: string }> = {
      draft: { label: '草稿', color: 'bg-gray-100 text-gray-700' },
      confirmed: { label: '已确认', color: 'bg-green-100 text-green-700' },
      reviewed: { label: '已审核', color: 'bg-blue-100 text-blue-700' },
    }
    return statuses[status] || { label: status, color: 'bg-gray-100 text-gray-700' }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 标题和操作栏 */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">批注管理</h2>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleExport('json')}
            className="flex items-center px-4 py-2 bg-white border rounded hover:bg-gray-50"
          >
            <FiDownload className="w-4 h-4 mr-2" />
            导出JSON
          </button>
          <button
            onClick={() => handleExport('csv')}
            className="flex items-center px-4 py-2 bg-white border rounded hover:bg-gray-50"
          >
            <FiDownload className="w-4 h-4 mr-2" />
            导出CSV
          </button>
        </div>
      </div>

      {/* 筛选栏 */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">搜索</label>
            <div className="relative">
              <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                placeholder="搜索文本..."
                className="w-full pl-10 pr-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">标注类型</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">全部类型</option>
              <option value="error_char">识别错误</option>
              <option value="missing">缺失内容</option>
              <option value="extra">多余内容</option>
              <option value="format">格式错误</option>
              <option value="unclear">模糊不清</option>
              <option value="other">其他问题</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">状态</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">全部状态</option>
              <option value="draft">草稿</option>
              <option value="confirmed">已确认</option>
              <option value="reviewed">已审核</option>
            </select>
          </div>
          <div className="flex items-end space-x-2">
            {selectedIds.size > 0 && (
              <>
                <button
                  onClick={handleBatchConfirm}
                  className="flex items-center px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  <FiCheck className="w-4 h-4 mr-2" />
                  确认 ({selectedIds.size})
                </button>
                <button
                  onClick={handleBatchDelete}
                  className="flex items-center px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  <FiTrash2 className="w-4 h-4 mr-2" />
                  删除 ({selectedIds.size})
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* 批注列表 */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedIds.size === paginatedAnnotations.length && paginatedAnnotations.length > 0}
                    onChange={handleSelectAll}
                    className="rounded"
                  />
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">原文</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">建议</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">章节</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">确信度</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedAnnotations.map((ann) => {
                const statusInfo = getStatusLabel(ann.status)
                
                return (
                  <tr key={ann.annotation_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(ann.annotation_id)}
                        onChange={() => handleSelect(ann.annotation_id)}
                        className="rounded"
                      />
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {ann.annotation_id.slice(0, 8)}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {getTypeLabel(ann.annotation_type)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate">
                      {ann.original_text}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate">
                      {ann.suggested_text || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {ann.chapter}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`font-medium ${(ann.confidence || 0) >= 0.8 ? 'text-green-600' : 'text-yellow-600'}`}>
                        {((ann.confidence || 0) * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 rounded text-xs ${statusInfo.color}`}>
                        {statusInfo.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(ann.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* 分页 */}
        <div className="bg-gray-50 px-4 py-3 flex items-center justify-between border-t">
          <div className="text-sm text-gray-700">
            共 {filteredAnnotations.length} 条批注
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded text-sm disabled:opacity-50"
            >
              上一页
            </button>
            <span className="text-sm">
              第 {currentPage} / {totalPages} 页
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 border rounded text-sm disabled:opacity-50"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
