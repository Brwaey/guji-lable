import { useState } from 'react'
import { FiX, FiCheck, FiAlertCircle } from 'react-icons/fi'
import { AnnotationCreate } from '@/services/annotationApi'

interface AnnotationEditorProps {
  chunk: {
    chunk_index: number
    chapter: string
    ocr_text: string
    ref_text?: string
    similarity: number
  }
  ocrFile: string
  refFile: string
  onSave: (annotation: AnnotationCreate) => void
  onCancel: () => void
}

const ANNOTATION_TYPES = [
  { code: 'error_char', name: '识别错误', icon: '🔴', description: '字符被错误识别为其他字符' },
  { code: 'missing', name: '缺失内容', icon: '📝', description: 'OCR遗漏的内容' },
  { code: 'extra', name: '多余内容', icon: '➕', description: 'OCR多识别的内容' },
  { code: 'format', name: '格式错误', icon: '⚠️', description: '标点、分段等格式问题' },
  { code: 'unclear', name: '模糊不清', icon: '🔍', description: '原图模糊导致无法识别' },
  { code: 'other', name: '其他问题', icon: '❓', description: '其他类型错误' },
]

export default function AnnotationEditor({
  chunk,
  ocrFile,
  refFile,
  onSave,
  onCancel,
}: AnnotationEditorProps) {
  const [annotationType, setAnnotationType] = useState('error_char')
  const [selectedText, setSelectedText] = useState('')
  const [selectionStart, setSelectionStart] = useState(0)
  const [selectionEnd, setSelectionEnd] = useState(0)
  const [suggestedText, setSuggestedText] = useState('')
  const [confidence, setConfidence] = useState(0.5)
  const [note, setNote] = useState('')
  const [isTextSelected, setIsTextSelected] = useState(false)

  const handleTextSelection = () => {
    const selection = window.getSelection()
    if (selection && selection.toString()) {
      const selected = selection.toString()
      setSelectedText(selected)
      setIsTextSelected(true)
      
      // 尝试获取位置（简化版本）
      const ocrTextElement = document.getElementById('ocr-text-area')
      if (ocrTextElement) {
        const textContent = ocrTextElement.textContent || ''
        const startIndex = textContent.indexOf(selected)
        if (startIndex !== -1) {
          setSelectionStart(startIndex)
          setSelectionEnd(startIndex + selected.length)
        }
      }
    }
  }

  const handleSubmit = (asDraft: boolean) => {
    if (!isTextSelected) {
      alert('请先在OCR文本中选择错误区域')
      return
    }

    const annotation: AnnotationCreate = {
      ocr_file: ocrFile,
      reference_file: refFile,
      chunk_index: chunk.chunk_index,
      chapter: chunk.chapter,
      annotation_type: annotationType,
      ocr_position: { start: selectionStart, end: selectionEnd },
      original_text: selectedText,
      suggested_text: suggestedText || undefined,
      confidence: confidence,
      note: note || undefined,
      ocr_text: chunk.ocr_text,
      ref_text: chunk.ref_text,
      similarity: chunk.similarity,
    }

    onSave(annotation)
  }

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.85) return 'bg-sim-excellent'
    if (similarity >= 0.70) return 'bg-sim-medium'
    return 'bg-sim-poor'
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full m-4 overflow-hidden">
        {/* 头部 */}
        <div className="bg-primary-600 text-white px-6 py-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold">新建标注</h3>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-white hover:bg-opacity-20 rounded transition-colors"
          >
            <FiX className="w-5 h-5" />
          </button>
        </div>

        {/* 内容区 */}
        <div className="p-6 max-h-[70vh] overflow-y-auto">
          {/* 文本块信息 */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">
                文本块 #{chunk.chunk_index} | 章节: {chunk.chapter}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSimilarityColor(chunk.similarity)}`}>
                相似度: {(chunk.similarity * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* 文本对比展示 */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            {/* OCR文本 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OCR识别结果（请选择错误区域）
              </label>
              <div
                id="ocr-text-area"
                className="p-4 bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg min-h-[150px] text-sm leading-relaxed select-text cursor-text"
                onMouseUp={handleTextSelection}
              >
                {chunk.ocr_text}
              </div>
              {isTextSelected && (
                <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm">
                  已选择: <strong className="text-yellow-800">{selectedText}</strong>
                </div>
              )}
            </div>

            {/* 参考文本 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                参考文本（Ground Truth）
              </label>
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg min-h-[150px] text-sm leading-relaxed">
                {chunk.ref_text || '无匹配文本'}
              </div>
            </div>
          </div>

          {/* 标注类型选择 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              标注类型
            </label>
            <div className="grid grid-cols-3 gap-2">
              {ANNOTATION_TYPES.map((type) => (
                <button
                  key={type.code}
                  onClick={() => setAnnotationType(type.code)}
                  className={`p-3 border rounded-lg text-left transition-colors ${
                    annotationType === type.code
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center mb-1">
                    <span className="text-lg mr-2">{type.icon}</span>
                    <span className="text-sm font-medium">{type.name}</span>
                  </div>
                  <p className="text-xs text-gray-500">{type.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* 修正建议 */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              修正建议（可选）
            </label>
            <input
              type="text"
              value={suggestedText}
              onChange={(e) => setSuggestedText(e.target.value)}
              placeholder="输入正确的文本..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* 确信度 */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              确信度
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={confidence}
                onChange={(e) => setConfidence(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-sm font-medium text-gray-700 w-12">
                {(confidence * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              表示您对此次标注的确定程度
            </p>
          </div>

          {/* 备注 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              备注（可选）
            </label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="添加额外的说明或备注..."
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />
          </div>

          {/* 提示信息 */}
          {!isTextSelected && (
            <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start">
              <FiAlertCircle className="w-5 h-5 text-yellow-600 mr-3 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-yellow-800">请在OCR文本中选择错误区域</p>
                <p className="text-yellow-600 mt-1">
                  使用鼠标在左侧OCR文本中拖动选择需要标注的错误部分
                </p>
              </div>
            </div>
          )}
        </div>

        {/* 底部按钮 */}
        <div className="bg-gray-50 px-6 py-4 flex items-center justify-between">
          <button
            onClick={onCancel}
            className="px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            取消
          </button>
          <div className="flex space-x-3">
            <button
              onClick={() => handleSubmit(false)}
              disabled={!isTextSelected}
              className={`px-6 py-2 rounded-lg font-medium ${
                !isTextSelected
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              保存草稿
            </button>
            <button
              onClick={() => handleSubmit(true)}
              disabled={!isTextSelected}
              className={`flex items-center px-6 py-2 rounded-lg font-medium ${
                !isTextSelected
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-primary-600 text-white hover:bg-primary-700'
              }`}
            >
              <FiCheck className="w-4 h-4 mr-2" />
              确认并提交
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}