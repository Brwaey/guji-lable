import { useState } from 'react'
import { FiEdit3, FiTrash2, FiEye, FiDownload, FiFilter } from 'react-icons/fi'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { annotationApi, Annotation, AnnotationListResponse } from '@/services/annotationApi'

export default function AnnotationPage() {
  const queryClient = useQueryClient()
  
  // 状态
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [selectedAnnotation, setSelectedAnnotation] = useState<Annotation | null>(null)
  
  // 获取标注列表
  const { data: annotationsData, isLoading } = useQuery<AnnotationListResponse>({
    queryKey: ['annotations', page, pageSize, statusFilter, typeFilter],
    queryFn: () => annotationApi.list({
      page,
      page_size: pageSize,
      status: statusFilter || undefined,
      annotation_type: typeFilter || undefined,
    }),
  })
  
  // 获取统计信息
  const { data: stats } = useQuery({
    queryKey: ['annotationStats'],
    queryFn: () => annotationApi.getStats(),
  })
  
  // 获取标注类型列表
  const { data: types } = useQuery({
    queryKey: ['annotationTypes'],
    queryFn: annotationApi.getTypes,
  })
  
  // 删除标注
  const deleteMutation = useMutation({
    mutationFn: annotationApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['annotations'] })
      queryClient.invalidateQueries({ queryKey: ['annotationStats'] })
      toast.success('标注已删除')
    },
    onError: (error: any) => {
      toast.error(`删除失败: ${error.response?.data?.detail || error.message}`)
    },
  })
  
  // 处理删除
  const handleDelete = (annotationId: string) => {
    if (confirm('确定要删除此标注吗？')) {
      deleteMutation.mutate(annotationId)
    }
  }
  
  // 导出标注
  const handleExport = async () => {
    try {
      const data = await annotationApi.export('json', 'all')
      
      // 创建下载
      const blob = new Blob([data], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = window.document.createElement('a')
      a.href = url
      a.download = `annotations_${new Date().toISOString().split('T')[0]}.json`
      window.document.body.appendChild(a)
      a.click()
      window.document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      toast.success('标注数据已导出')
    } catch (error: any) {
      toast.error(`导出失败: ${error.message}`)
    }
  }
  
  // 查看标注详情
  const handleView = (annotation: Annotation) => {
    setSelectedAnnotation(annotation)
  }
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'draft':
        return 'bg-gray-100 text-gray-700'
      case 'confirmed':
        return 'bg-green-100 text-green-700'
      case 'reviewed':
        return 'bg-blue-100 text-blue-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }
  
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'error_char': return '🔴'
      case 'missing': return '📝'
      case 'extra': return '➕'
      case 'format': return '⚠️'
      case 'unclear': return '🔍'
      case 'other': return '❓'
      default: return '❓'
    }
  }
  
  return (
    <div className="space-y-6">
      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">总标注数</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.total_annotations || 0}
              </p>
            </div>
            <FiEdit3 className="w-8 h-8 text-primary-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">平均确信度</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.avg_confidence ? `${(stats.avg_confidence * 100).toFixed(0)}%` : '0%'}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 text-xl">✓</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">已确认</p>
              <p className="text-2xl font-bold text-green-600">
                {stats?.by_status?.confirmed || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 text-xl">✓</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">已审核</p>
              <p className="text-2xl font-bold text-blue-600">
                {stats?.by_status?.reviewed || 0}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 text-xl">✓</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* 按类型统计 */}
      {stats?.by_type && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">按类型统计</h3>
          <div className="grid grid-cols-6 gap-4">
            {types?.map((type: any) => {
              const count = stats.by_type[type.code] || 0
              return (
                <div key={type.code} className="text-center">
                  <div className="w-16 h-16 mx-auto mb-2 bg-gray-50 rounded-full flex items-center justify-center">
                    <span className="text-2xl">{type.icon || getTypeIcon(type.code)}</span>
                  </div>
                  <p className="text-sm font-medium text-gray-900">{type.name}</p>
                  <p className="text-lg font-bold text-primary-600">{count}</p>
                </div>
              )
            })}
          </div>
        </div>
      )}
      
      {/* 过滤器和操作 */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* 状态过滤 */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">全部状态</option>
              <option value="draft">草稿</option>
              <option value="confirmed">已确认</option>
              <option value="reviewed">已审核</option>
            </select>
            
            {/* 类型过滤 */}
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">全部类型</option>
              {types?.map((type: any) => (
                <option key={type.code} value={type.code}>
                  {type.icon} {type.name}
                </option>
              ))}
            </select>
            
            {/* 重置过滤器 */}
            <button
              onClick={() => {
                setStatusFilter('')
                setTypeFilter('')
                setPage(1)
              }}
              className="px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg flex items-center"
            >
              <FiFilter className="w-4 h-4 mr-2" />
              重置
            </button>
          </div>
          
          {/* 导出按钮 */}
          <button
            onClick={handleExport}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center"
          >
            <FiDownload className="w-4 h-4 mr-2" />
            导出标注
          </button>
        </div>
      </div>
      
      {/* 标注列表 */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">
            加载中...
          </div>
        ) : annotationsData && annotationsData.annotations.length > 0 ? (
          <>
            {/* 表格 */}
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    标注ID
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    类型
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    章节
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    原文
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    状态
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    确信度
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    创建时间
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {annotationsData.annotations.map((annotation) => (
                  <tr key={annotation.annotation_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {annotation.annotation_id}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className="flex items-center">
                        <span className="mr-2">{getTypeIcon(annotation.annotation_type)}</span>
                        {types?.find((t: any) => t.code === annotation.annotation_type)?.name || annotation.annotation_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {annotation.chapter}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate">
                      {annotation.original_text}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(annotation.status)}`}>
                        {annotation.status === 'draft' ? '草稿' : annotation.status === 'confirmed' ? '已确认' : '已审核'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {(annotation.confidence * 100).toFixed(0)}%
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(annotation.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleView(annotation)}
                          className="p-2 text-gray-600 hover:bg-gray-100 rounded"
                          title="查看详情"
                        >
                          <FiEye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(annotation.annotation_id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded"
                          title="删除"
                        >
                          <FiTrash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {/* 分页 */}
            <div className="bg-gray-50 px-4 py-3 flex items-center justify-between">
              <div className="text-sm text-gray-500">
                显示 {(page - 1) * pageSize + 1} - {Math.min(page * pageSize, annotationsData.total)} 条，共 {annotationsData.total} 条
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className={`px-3 py-1 rounded ${
                    page === 1
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-white border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  上一页
                </button>
                <span className="text-sm text-gray-700">
                  第 {page} 页
                </span>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page * pageSize >= annotationsData.total}
                  className={`px-3 py-1 rounded ${
                    page * pageSize >= annotationsData.total
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-white border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  下一页
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="p-8 text-center text-gray-500">
            <FiEdit3 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium text-gray-900 mb-2">暂无标注数据</p>
            <p className="text-sm">
              请在"文本对比"页面进行标注，或调整筛选条件
            </p>
          </div>
        )}
      </div>
      
      {/* 详情弹窗 */}
      {selectedAnnotation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full m-4 overflow-hidden">
            <div className="bg-primary-600 text-white px-6 py-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold">标注详情</h3>
              <button
                onClick={() => setSelectedAnnotation(null)}
                className="p-2 hover:bg-white hover:bg-opacity-20 rounded"
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
              {/* 基本信息 */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">标注ID</label>
                  <p className="text-sm text-gray-900">{selectedAnnotation.annotation_id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">状态</label>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(selectedAnnotation.status)}`}>
                    {selectedAnnotation.status === 'draft' ? '草稿' : selectedAnnotation.status === 'confirmed' ? '已确认' : '已审核'}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">标注类型</label>
                  <p className="text-sm text-gray-900 flex items-center">
                    <span className="mr-2">{getTypeIcon(selectedAnnotation.annotation_type)}</span>
                    {types?.find((t: any) => t.code === selectedAnnotation.annotation_type)?.name || selectedAnnotation.annotation_type}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">章节</label>
                  <p className="text-sm text-gray-900">{selectedAnnotation.chapter}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">OCR文件</label>
                  <p className="text-sm text-gray-900 truncate">{selectedAnnotation.ocr_file}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">参考文件</label>
                  <p className="text-sm text-gray-900 truncate">{selectedAnnotation.reference_file}</p>
                </div>
              </div>
              
              {/* 文本对比 */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">原文（错误部分）</label>
                  <div className="p-3 bg-red-50 border border-red-200 rounded text-sm">
                    {selectedAnnotation.original_text}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">修正建议</label>
                  <div className="p-3 bg-green-50 border border-green-200 rounded text-sm">
                    {selectedAnnotation.suggested_text || '未提供'}
                  </div>
                </div>
              </div>
              
              {/* OCR完整文本 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">OCR完整文本</label>
                <div className="p-3 bg-gray-50 border border-gray-200 rounded text-sm max-h-100 overflow-y-auto">
                  {selectedAnnotation.ocr_text}
                </div>
              </div>
              
              {/* 其他信息 */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">确信度</label>
                  <p className="text-sm text-gray-900">{(selectedAnnotation.confidence * 100).toFixed(0)}%</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">相似度</label>
                  <p className="text-sm text-gray-900">
                    {selectedAnnotation.similarity ? `${(selectedAnnotation.similarity * 100).toFixed(1)}%` : '未计算'}
                  </p>
                </div>
              </div>
              
              {selectedAnnotation.note && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">备注</label>
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded text-sm">
                    {selectedAnnotation.note}
                  </div>
                </div>
              )}
              
              {/* 时间信息 */}
              <div className="grid grid-cols-2 gap-4 text-sm text-gray-500">
                <div>创建时间: {new Date(selectedAnnotation.created_at).toLocaleString()}</div>
                <div>更新时间: {new Date(selectedAnnotation.updated_at).toLocaleString()}</div>
              </div>
            </div>
            
            <div className="bg-gray-50 px-6 py-4">
              <button
                onClick={() => setSelectedAnnotation(null)}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}