import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FiEdit3 } from 'react-icons/fi'
import FileBrowser from '@/components/FileBrowser/FileBrowser'
import AnnotationEditor from '@/components/Annotation/AnnotationEditor'
import { fileApi } from '@/services/fileApi'
import { similarityApi, SimilarityResult, TaskStatus } from '@/services/similarityApi'
import { annotationApi, AnnotationCreate } from '@/services/annotationApi'
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
  const [selectedChunk, setSelectedChunk] = useState<TextChunk | null>(null)
  const [showAnnotationEditor, setShowAnnotationEditor] = useState(false)

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
        } else if (status.status === 'processing') {
          // 继续轮询
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

  // 打开批注编辑器
  const handleOpenAnnotation = (chunk: TextChunk) => {
    setSelectedChunk(chunk)
    setShowAnnotationEditor(true)
  }

  // 保存批注
  const handleSaveAnnotation = async (annotation: AnnotationCreate) => {
    try {
      await annotationApi.create(annotation)
      toast.success('批注保存成功！')
      setShowAnnotationEditor(false)
      setSelectedChunk(null)
    } catch (error: any) {
      toast.error(`保存失败: ${error.response?.data?.detail || error.message}`)
    }
  }

  return (
    <div className="space-y-6">
      {/* 文件选择区 */}
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

      {/* 已选择的文件 */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-2 gap-4 mb-4">
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

        {/* 开始计算按钮 */}
        <button
          onClick={handleCompute}
          disabled={!ocrFile || !refFile || isComputing}
          className={`w-full py-3 rounded-lg font-medium ${
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

      {/* 计算结果展示 */}
      {result && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">计算结果</h3>

          {/* 整体统计 */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-primary-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">整体相似度</p>
              <p className="text-2xl font-bold text-primary-600">
                {(result.overall_similarity * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">总文本块</p>
              <p className="text-2xl font-bold text-gray-900">{result.total_chunks}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">高质量匹配</p>
              <p className="text-2xl font-bold text-green-600">{result.matched_chunks}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">处理耗时</p>
              <p className="text-2xl font-bold text-gray-900">
                {result.processing_time.toFixed(1)}s
              </p>
            </div>
          </div>

          {/* 章节统计 */}
          {result.chapter_stats.length > 0 && (
            <div className="mb-6">
              <h4 className="text-md font-semibold text-gray-900 mb-2">章节统计</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        章节名称
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        文本块数
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        平均相似度
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        低质量块数
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {result.chapter_stats.map((stat, idx) => (
                      <tr key={idx}>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {stat.chapter_name}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {stat.total_chunks}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <div className="flex items-center">
                            <div className="w-16 h-2 bg-gray-200 rounded-full mr-2">
                              <div
                                className={`h-full rounded-full ${
                                  stat.avg_similarity >= 0.85
                                    ? 'bg-sim-excellent'
                                    : stat.avg_similarity >= 0.7
                                    ? 'bg-sim-medium'
                                    : 'bg-sim-poor'
                                }`}
                                style={{ width: `${stat.avg_similarity * 100}%` }}
                              />
                            </div>
                            <span className="text-gray-900">
                              {(stat.avg_similarity * 100).toFixed(1)}%
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {stat.low_similarity_count}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 文本块对比（前20个） */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-2">文本块对比（前20个）</h4>
            <div className="space-y-2 max-h-600 overflow-y-auto">
              {result.chunks.slice(0, 20).map((chunk) => (
                <div
                  key={chunk.chunk_index}
                  className={`border rounded-lg p-3 ${
                    chunk.similarity >= 0.85
                      ? 'bg-sim-excellent'
                      : chunk.similarity >= 0.7
                      ? 'bg-sim-medium'
                      : 'bg-sim-poor'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-gray-600">
                      块 #{chunk.chunk_index} | {chunk.chapter}
                    </span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-bold">
                        {(chunk.similarity * 100).toFixed(1)}%
                      </span>
                      <button
                        onClick={() => handleOpenAnnotation(chunk)}
                        className="flex items-center px-2 py-1 bg-white bg-opacity-50 hover:bg-opacity-80 rounded text-xs font-medium text-gray-700 transition-colors"
                        title="添加批注"
                      >
                        <FiEdit3 className="w-3 h-3 mr-1" />
                        批注
                      </button>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-white bg-opacity-50 rounded p-2">
                      <p className="font-medium text-gray-700 mb-1">OCR:</p>
                      <p className="text-gray-900 line-clamp-3">{chunk.ocr_text}</p>
                    </div>
                    <div className="bg-white bg-opacity-50 rounded p-2">
                      <p className="font-medium text-gray-700 mb-1">参考:</p>
                      <p className="text-gray-900 line-clamp-3">
                        {chunk.ref_text || '无匹配'}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 批注编辑器弹窗 */}
      {showAnnotationEditor && selectedChunk && (
        <AnnotationEditor
          chunk={selectedChunk}
          ocrFile={ocrFile}
          refFile={refFile}
          onSave={handleSaveAnnotation}
          onCancel={() => {
            setShowAnnotationEditor(false)
            setSelectedChunk(null)
          }}
        />
      )}
    </div>
  )
}