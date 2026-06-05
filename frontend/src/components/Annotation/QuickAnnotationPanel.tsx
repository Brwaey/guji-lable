import { useState } from 'react'
import { FiX, FiCheck, FiMessageCircle } from 'react-icons/fi'

interface QuickAnnotationPanelProps {
  chunk: {
    chunk_index: number
    chapter: string
    ocr_text: string
    ref_text?: string
    similarity: number
  }
  ocrFile: string
  refFile: string
  onSave: (annotation: any) => Promise<void>
  onClose: () => void
  existingAnnotations?: any[]
}

const ANNOTATION_TYPES = [
  { code: 'error_char', name: '识别错误', icon: '🔴', requiresOcr: true, requiresRef: false },
  { code: 'missing', name: '缺失内容', icon: '📝', requiresOcr: false, requiresRef: true },
  { code: 'extra', name: '多余内容', icon: '➕', requiresOcr: true, requiresRef: false },
  { code: 'format', name: '格式错误', icon: '⚠️', requiresOcr: true, requiresRef: false },
  { code: 'unclear', name: '模糊不清', icon: '🔍', requiresOcr: true, requiresRef: false },
  { code: 'other', name: '其他问题', icon: '❓', requiresOcr: false, requiresRef: false },
]

export default function QuickAnnotationPanel({
  chunk,
  ocrFile,
  refFile,
  onSave,
  onClose,
  existingAnnotations = [],
}: QuickAnnotationPanelProps) {
  const [annotationType, setAnnotationType] = useState('error_char')
  const [ocrSelection, setOcrSelection] = useState<{ text: string; start: number; end: number } | null>(null)
  const [refSelection, setRefSelection] = useState<{ text: string; start: number; end: number } | null>(null)
  const [suggestedText, setSuggestedText] = useState('')
  const [confidence, setConfidence] = useState(0.8)
  const [note, setNote] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  const currentType = ANNOTATION_TYPES.find(t => t.code === annotationType)

  const handleOcrTextSelection = () => {
    const selection = window.getSelection()
    if (selection && selection.toString()) {
      const selected = selection.toString()
      const ocrTextElement = document.getElementById(`ocr-text-${chunk.chunk_index}-${chunk.chapter}`)
      if (ocrTextElement) {
        const textContent = ocrTextElement.textContent || ''
        const startIndex = textContent.indexOf(selected)
        if (startIndex !== -1) {
          setOcrSelection({
            text: selected,
            start: startIndex,
            end: startIndex + selected.length,
          })
        }
      }
    }
  }

  const handleRefTextSelection = () => {
    const selection = window.getSelection()
    if (selection && selection.toString()) {
      const selected = selection.toString()
      const refTextElement = document.getElementById(`ref-text-${chunk.chunk_index}-${chunk.chapter}`)
      if (refTextElement) {
        const textContent = refTextElement.textContent || ''
        const startIndex = textContent.indexOf(selected)
        if (startIndex !== -1) {
          setRefSelection({
            text: selected,
            start: startIndex,
            end: startIndex + selected.length,
          })
        }
      }
    }
  }

  const canSave = () => {
    if (!currentType) return false
    
    // 缺失内容：需要选择参考文本
    if (annotationType === 'missing') {
      return refSelection !== null
    }
    
    // 其他类型：需要选择OCR文本
    return ocrSelection !== null
  }

  const handleSubmit = async () => {
    if (!canSave()) return

    setIsSaving(true)
    try {
      const annotation = {
        ocr_file: ocrFile,
        reference_file: refFile,
        chunk_index: chunk.chunk_index,
        chapter: chunk.chapter,
        annotation_type: annotationType,
        ocr_position: ocrSelection ? { start: ocrSelection.start, end: ocrSelection.end } : { start: 0, end: 0 },
        original_text: ocrSelection?.text || refSelection?.text || '',
        suggested_text: suggestedText || undefined,
        confidence: confidence,
        note: note || undefined,
        ocr_text: chunk.ocr_text,
        ref_text: chunk.ref_text,
        similarity: chunk.similarity,
        // 如果是缺失内容，标记为参考文本选择
        is_ref_selection: annotationType === 'missing' && refSelection !== null,
        ref_position: refSelection ? { start: refSelection.start, end: refSelection.end } : undefined,
      }

      await onSave(annotation)
      setSaveSuccess(true)
      
      // 清空选择
      setOcrSelection(null)
      setRefSelection(null)
      setSuggestedText('')
      setNote('')
      
      // 2秒后关闭
      setTimeout(() => {
        setSaveSuccess(false)
      }, 2000)
    } catch (error) {
      console.error('保存失败:', error)
      alert('保存失败，请重试')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="bg-white border-l-2 border-primary-500 h-full flex flex-col">
      {/* 头部 */}
      <div className="bg-primary-600 text-white px-4 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center">
          <FiMessageCircle className="w-5 h-5 mr-2" />
          <span className="font-semibold">快速批注</span>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-white hover:bg-opacity-20 rounded">
          <FiX className="w-5 h-5" />
        </button>
      </div>

      {/* 内容区 - 可滚动 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* 文本块信息 */}
        <div className="bg-gray-50 rounded p-3">
          <div className="text-sm text-gray-600">
            文本块 #{chunk.chunk_index}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            章节: {chunk.chapter}
          </div>
          <div className="text-xs mt-1">
            相似度: <span className={`font-bold ${chunk.similarity >= 0.85 ? 'text-green-600' : chunk.similarity >= 0.7 ? 'text-yellow-600' : 'text-red-600'}`}>
              {(chunk.similarity * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        {/* 标注类型 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">标注类型</label>
          <div className="grid grid-cols-2 gap-2">
            {ANNOTATION_TYPES.map(type => (
              <button
                key={type.code}
                onClick={() => setAnnotationType(type.code)}
                className={`p-2 border-2 rounded text-left transition-colors text-sm ${
                  annotationType === type.code
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <span className="mr-1">{type.icon}</span>
                {type.name}
              </button>
            ))}
          </div>
        </div>

        {/* 文本对比展示 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            文本对比
          </label>
          <div className="grid grid-cols-2 gap-2">
            {/* OCR文本 */}
            <div>
              <div className="mb-1">
                <span className="text-xs font-medium text-gray-600">OCR识别结果</span>
              </div>
              {annotationType !== 'missing' && (
                <div className="mb-1 text-xs text-primary-600 font-medium">
                  ← 在下方白色区域拖动选择文本
                </div>
              )}
              <div
                id={`ocr-text-${chunk.chunk_index}-${chunk.chapter}`}
                className={`p-3 border-2 rounded min-h-[120px] text-sm ${
                  annotationType === 'missing' 
                    ? 'bg-gray-100 border-gray-200 text-gray-400 no-select' 
                    : 'bg-white border-primary-300 hover:border-primary-500 selectable-text'
                }`}
                onMouseUp={handleOcrTextSelection}
              >
                {chunk.ocr_text}
              </div>
              {ocrSelection && annotationType !== 'missing' && (
                <div className="mt-2 p-2 bg-yellow-50 border-2 border-yellow-300 rounded text-xs">
                  <span className="font-medium text-yellow-800">✓ 已选择：</span>
                  <span className="text-yellow-900 font-semibold">{ocrSelection.text}</span>
                </div>
              )}
            </div>

            {/* 参考文本 */}
            <div>
              <div className="mb-1">
                <span className="text-xs font-medium text-gray-600">参考文本（正确答案）</span>
              </div>
              {annotationType === 'missing' && (
                <div className="mb-1 text-xs text-primary-600 font-medium">
                  ← 在下方绿色区域拖动选择文本
                </div>
              )}
              <div
                id={`ref-text-${chunk.chunk_index}-${chunk.chapter}`}
                className={`p-3 border-2 rounded min-h-[120px] text-sm ${
                  annotationType === 'missing' 
                    ? 'bg-green-50 border-green-300 hover:border-green-500 selectable-text' 
                    : 'bg-gray-50 border-gray-200 no-select'
                }`}
                onMouseUp={handleRefTextSelection}
              >
                {chunk.ref_text || '无匹配'}
              </div>
              {refSelection && annotationType === 'missing' && (
                <div className="mt-2 p-2 bg-green-100 border-2 border-green-300 rounded text-xs">
                  <span className="font-medium text-green-800">✓ 已选择：</span>
                  <span className="text-green-900 font-semibold">{refSelection.text}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 修正建议 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            修正建议
          </label>
          <input
            type="text"
            value={suggestedText}
            onChange={(e) => setSuggestedText(e.target.value)}
            placeholder="输入正确的文本..."
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* 确信度 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            确信度: {(confidence * 100).toFixed(0)}%
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={confidence}
            onChange={(e) => setConfidence(parseFloat(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* 备注 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">备注</label>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="添加备注说明..."
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
          />
        </div>

        {/* 保存按钮 - 紧贴备注下方 */}
        <div className="space-y-2">
          {saveSuccess && (
            <div className="bg-green-50 border-2 border-green-300 rounded p-2 text-center text-sm text-green-700 flex items-center justify-center">
              <FiCheck className="w-4 h-4 mr-2" />
              保存成功！继续批注
            </div>
          )}
          
          <button
            onClick={handleSubmit}
            disabled={!canSave() || isSaving}
            className={`w-full py-3 rounded-lg font-medium transition-colors ${
              !canSave()
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : isSaving
                ? 'bg-primary-400 text-white cursor-wait'
                : 'bg-primary-600 text-white hover:bg-primary-700'
            }`}
          >
            {isSaving ? '保存中...' : '保存批注'}
          </button>
          
          {!canSave() && (
            <p className="text-xs text-red-500 text-center">
              请先选择需要标注的文本
            </p>
          )}
        </div>

        {/* 已有批注 */}
        {existingAnnotations.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              已有批注 ({existingAnnotations.length})
            </label>
            <div className="space-y-2">
              {existingAnnotations.map((ann, idx) => (
                <div key={idx} className="bg-gray-50 border rounded p-2 text-sm">
                  <div className="font-medium">{ann.annotation_type}</div>
                  <div className="text-gray-600 text-xs mt-1">{ann.original_text}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
