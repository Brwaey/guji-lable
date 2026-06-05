import { useState, useEffect, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FiEdit3, FiCheck, FiChevronLeft, FiChevronRight } from 'react-icons/fi'
import FileBrowser from '@/components/FileBrowser/FileBrowser'
import QuickAnnotationPanel from '@/components/Annotation/QuickAnnotationPanel'
import { fileApi } from '@/services/fileApi'
import { similarityApi, SimilarityResult, TaskStatus } from '@/services/similarityApi'
import { annotationApi } from '@/services/annotationApi'
import toast from 'react-hot-toast'

interface TextChunk {
  chunk_index: number
  chapter: string
  ocr_text: string
  ref_text?: string
  similarity: number
}

export default function ComparePage() {
  const [ocrFile, setOcrFile] = useState<string>('')
  const [refFile, setRefFile] = useState<string>('')
  const [taskId, setTaskId] = useState<string>('')
  const [isComputing, setIsComputing] = useState(false)
  const [result, setResult] = useState<SimilarityResult | null>(null)
  
  // 批注相关状态
  const [selectedChunkIndex, setSelectedChunkIndex] = useState<number | null>(null)
  const [showAnnotationPanel, setShowAnnotationPanel] = useState(false)
  const [chunkAnnotations, setChunkAnnotations] = useState<Map<number, any[]>>(new Map())
  
  // 分页状态
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(50) // 每页50个文本块

  // 获取基础路径
  const { data: basePaths } = useQuery({
    queryKey: ['basePaths'],
    queryFn: fileApi.getBasePaths,
  })

  // 监听任务状态
  useEffect(() => {
    if (!taskId || !isComputing) return

    const pollStatus = async () => {
      try {
        const status: TaskStatus = await similarityApi.getStatus(taskId)

        if (status.status === 'completed') {
          setIsComputing(false)
          const resultData = await similarityApi.getResultDetail(taskId)
          setResult(resultData)
          toast.success('相似度计算完成！')
        } else if (status.status === 'failed') {
          setIsComputing(false)
          toast.error(`计算失败: ${status.message || '未知错误'}`)
        }
      } catch (error) {
        console.error('获取状态失败:', error)
      }
    }

    const interval = setInterval(pollStatus, 2000)
    return () => clearInterval(interval)
  }, [taskId, isComputing])

  // 开始计算
  const handleCompute = async () => {
    if (!ocrFile || !refFile) {
      toast.error('请先选择OCR文件和参考文本')
      return
    }

    setIsComputing(true)
    setResult(null)
    setSelectedChunkIndex(null)
    setShowAnnotationPanel(false)

    try {
      const response = await similarityApi.compute({
        ocr_file: ocrFile,
        reference_file: refFile,
      })
      setTaskId(response.task_id)
      toast.success('开始计算相似度...')
    } catch (error: any) {
      setIsComputing(false)
      toast.error(`启动失败: ${error.response?.data?.detail || error.message}`)
    }
  }

  // 打开批注面板
  const handleOpenAnnotation = (chunkIndex: number) => {
    setSelectedChunkIndex(chunkIndex)
    setShowAnnotationPanel(true)
  }

  // 保存批注
  const handleSaveAnnotation = async (annotation: any) => {
    try {
      await annotationApi.create(annotation)
      
      // 更新本地批注列表
      const chunkIndex = annotation.chunk_index
      setChunkAnnotations(prev => {
        const newMap = new Map(prev)
        const annotations = newMap.get(chunkIndex) || []
        newMap.set(chunkIndex, [...annotations, annotation])
        return newMap
      })
      
      toast.success('批注保存成功！')
    } catch (error: any) {
      throw error
    }
  }

  // 关闭批注面板
  const handleCloseAnnotation = () => {
    setShowAnnotationPanel(false)
  }

  // 切换到下一个文本块
  const handleNextChunk = () => {
    if (result && selectedChunkIndex !== null && selectedChunkIndex < result.chunks.length - 1) {
      setSelectedChunkIndex(selectedChunkIndex + 1)
    }
  }

  // 切换到上一个文本块
  const handlePrevChunk = () => {
    if (selectedChunkIndex !== null && selectedChunkIndex > 0) {
      setSelectedChunkIndex(selectedChunkIndex - 1)
    }
  }

  // 计算分页数据
  const paginatedChunks = useMemo(() => {
    if (!result) return []
    const start = (currentPage - 1) * pageSize
    const end = start + pageSize
    return result.chunks.slice(start, end)
  }, [result, currentPage, pageSize])

  const totalPages = useMemo(() => {
    if (!result) return 0
    return Math.ceil(result.chunks.length / pageSize)
  }, [result, pageSize])

  const selectedChunk = useMemo(() => {
    if (!result || selectedChunkIndex === null) return null
    return result.chunks[selectedChunkIndex]
  }, [result, selectedChunkIndex])

  return (
    <div className="h-full flex flex-col">
      {/* 文件选择区 */}
      <div className="flex-shrink-0 bg-white border-b p-4">
        <div className="grid grid-cols-2 gap-6">
          <FileBrowser
            title="OCR文件"
            basePaths={basePaths?.ocr_paths || []}
            onSelectFile={setOcrFile}
          />
          <FileBrowser
            title="参考文本"
            basePaths={basePaths?.reference_path ? [basePaths.reference_path] : []}
            onSelectFile={setRefFile}
          />
        </div>

        <div className="mt-4 flex items-center justify-between">
          <div className="grid grid-cols-2 gap-4 flex-1 mr-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                已选择OCR文件
              </label>
              <div className="px-3 py-2 bg-gray-50 rounded text-sm text-gray-900 truncate">
                {ocrFile || '未选择'}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                已选择参考文本
              </label>
              <div className="px-3 py-2 bg-gray-50 rounded text-sm text-gray-900 truncate">
                {refFile || '未选择'}
              </div>
            </div>
          </div>

          <button
            onClick={handleCompute}
            disabled={!ocrFile || !refFile || isComputing}
            className={`px-6 py-3 rounded-lg font-medium ${
              !ocrFile || !refFile
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : isComputing
                ? 'bg-primary-200 text-primary-700 cursor-wait'
                : 'bg-primary-600 text-white hover:bg-primary-700'
            }`}
          >
            {isComputing ? '计算中...' : '开始计算相似度'}
          </button>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧：计算结果 */}
        <div className={`flex-1 overflow-hidden ${showAnnotationPanel ? 'pr-0' : ''}`}>
          {result && (
            <div className="h-full flex flex-col bg-gray-50 p-4">
              {/* 整体统计 */}
              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-600">整体相似度</p>
                  <p className="text-2xl font-bold text-primary-600">
                    {(result.overall_similarity * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-600">总文本块</p>
                  <p className="text-2xl font-bold text-gray-900">{result.total_chunks}</p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-600">高质量匹配</p>
                  <p className="text-2xl font-bold text-green-600">{result.matched_chunks}</p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow">
                  <p className="text-sm text-gray-600">批注数量</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {Array.from(chunkAnnotations.values()).reduce((sum, arr) => sum + arr.length, 0)}
                  </p>
                </div>
              </div>

              {/* 文本块列表 */}
              <div className="flex-1 overflow-hidden flex flex-col">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-md font-semibold text-gray-900">
                    文本块对比（共 {result.total_chunks} 块）
                  </h3>
                  
                  {/* 分页控制 */}
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setCurrentPage(1)}
                      disabled={currentPage === 1}
                      className="px-2 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                    >
                      首页
                    </button>
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="px-2 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                    >
                      <FiChevronLeft />
                    </button>
                    <span className="text-sm text-gray-600">
                      第 {currentPage} / {totalPages} 页
                    </span>
                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="px-2 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                    >
                      <FiChevronRight />
                    </button>
                    <button
                      onClick={() => setCurrentPage(totalPages)}
                      disabled={currentPage === totalPages}
                      className="px-2 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                    >
                      末页
                    </button>
                    
                    <select
                      value={pageSize}
                      onChange={(e) => {
                        setPageSize(Number(e.target.value))
                        setCurrentPage(1)
                      }}
                      className="ml-4 px-2 py-1 border rounded text-sm"
                    >
                      <option value={20}>20条/页</option>
                      <option value={50}>50条/页</option>
                      <option value={100}>100条/页</option>
                      <option value={200}>200条/页</option>
                    </select>
                  </div>
                </div>

                {/* 文本块网格 */}
                <div className="flex-1 overflow-y-auto space-y-2 pr-2">
                  {paginatedChunks.map((chunk) => {
                    const hasAnnotation = chunkAnnotations.has(chunk.chunk_index)
                    const isSelected = selectedChunkIndex === chunk.chunk_index
                    
                    return (
                      <div
                        key={chunk.chunk_index}
                        className={`border rounded-lg p-3 transition-all cursor-pointer ${
                          isSelected
                            ? 'border-primary-500 border-2 bg-primary-50'
                            : hasAnnotation
                            ? 'border-blue-400 bg-blue-50'
                            : chunk.similarity >= 0.85
                            ? 'bg-sim-excellent'
                            : chunk.similarity >= 0.7
                            ? 'bg-sim-medium'
                            : 'bg-sim-poor'
                        }`}
                        onClick={() => handleOpenAnnotation(chunk.chunk_index)}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-medium text-gray-600">
                            块 #{chunk.chunk_index} | {chunk.chapter}
                          </span>
                          <div className="flex items-center space-x-2">
                            {hasAnnotation && (
                              <span className="flex items-center px-2 py-1 bg-blue-500 text-white rounded text-xs">
                                <FiCheck className="w-3 h-3 mr-1" />
                                已批注
                              </span>
                            )}
                            <span className="text-sm font-bold">
                              {(chunk.similarity * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div className="bg-white bg-opacity-60 rounded p-2">
                            <p className="font-medium text-gray-700 mb-1">OCR:</p>
                            <p className="text-gray-900 line-clamp-2">{chunk.ocr_text}</p>
                          </div>
                          <div className="bg-white bg-opacity-60 rounded p-2">
                            <p className="font-medium text-gray-700 mb-1">参考:</p>
                            <p className="text-gray-900 line-clamp-2">
                              {chunk.ref_text || '无匹配'}
                            </p>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 右侧：批注面板 */}
        {showAnnotationPanel && selectedChunk && (
          <div className="w-96 flex-shrink-0 border-l bg-white">
            <QuickAnnotationPanel
              chunk={selectedChunk}
              ocrFile={ocrFile}
              refFile={refFile}
              onSave={handleSaveAnnotation}
              onClose={handleCloseAnnotation}
              existingAnnotations={chunkAnnotations.get(selectedChunk.chunk_index) || []}
            />
            
            {/* 快捷导航 */}
            <div className="border-t p-2 flex items-center justify-between bg-gray-50">
              <button
                onClick={handlePrevChunk}
                disabled={selectedChunkIndex === 0}
                className="flex items-center px-3 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                <FiChevronLeft className="w-4 h-4 mr-1" />
                上一块
              </button>
              <span className="text-xs text-gray-500">
                {selectedChunkIndex! + 1} / {result?.total_chunks}
              </span>
              <button
                onClick={handleNextChunk}
                disabled={selectedChunkIndex === result!.chunks.length - 1}
                className="flex items-center px-3 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                下一块
                <FiChevronRight className="w-4 h-4 ml-1" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
