import apiClient from './api'

export interface SimilarityComputeRequest {
  ocr_file: string
  reference_file: string
  options?: any
}

export interface TaskStatus {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress: number
  message?: string
  created_at: string
  updated_at: string
}

export interface TextChunk {
  chunk_index: number
  chapter: string
  ocr_text: string
  ref_text?: string
  similarity: number
  position: { start: number; end: number }
}

export interface SimilarityResult {
  overall_similarity: number
  total_chunks: number
  matched_chunks: number
  processing_time: number
  chunks: TextChunk[]
  chapter_stats: any[]
}

export const similarityApi = {
  // 开始计算
  compute: async (request: SimilarityComputeRequest): Promise<{ task_id: string }> => {
    const response = await apiClient.post('/similarity/compute', request)
    return response.data
  },

  // 获取任务状态
  getStatus: async (taskId: string): Promise<TaskStatus> => {
    const response = await apiClient.get(`/similarity/status/${taskId}`)
    return response.data
  },

  // 获取结果
  getResult: async (taskId: string): Promise<{ status: string; result?: SimilarityResult; error?: string }> => {
    const response = await apiClient.get(`/similarity/result/${taskId}`)
    return response.data
  },

  // 获取详细结果
  getResultDetail: async (taskId: string): Promise<SimilarityResult> => {
    const response = await apiClient.get(`/similarity/result/${taskId}/detail`)
    return response.data
  },

  // 检查API状态
  checkApiStatus: async (): Promise<any> => {
    const response = await apiClient.get('/similarity/api-status')
    return response.data
  },

  // 取消任务
  cancelTask: async (taskId: string): Promise<void> => {
    await apiClient.delete(`/similarity/task/${taskId}`)
  },
}