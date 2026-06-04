import apiClient from './api'

export interface AnnotationCreate {
  ocr_file: string
  reference_file: string
  chunk_index: number
  chapter: string
  annotation_type: string
  ocr_position: { start: number; end: number }
  original_text: string
  suggested_text?: string
  confidence?: number
  note?: string
  ocr_text?: string
  ref_text?: string
  similarity?: number
}

export interface Annotation {
  annotation_id: string
  ocr_file: string
  reference_file: string
  chunk_index: number
  chapter: string
  annotation_type: string
  ocr_position: { start: number; end: number }
  original_text: string
  suggested_text?: string
  confidence: number
  note?: string
  ocr_text?: string
  ref_text?: string
  similarity?: number
  annotator?: string
  status: string
  created_at: string
  updated_at: string
}

export interface AnnotationListResponse {
  annotations: Annotation[]
  total: number
  page: number
  page_size: number
}

export interface AnnotationStats {
  total_annotations: number
  by_type: Record<string, number>
  by_status: Record<string, number>
  by_chapter?: Record<string, number>
  avg_confidence: number
}

export const annotationApi = {
  // 创建标注
  create: async (data: AnnotationCreate): Promise<Annotation> => {
    const response = await apiClient.post('/annotations/create', data)
    return response.data
  },

  // 获取标注
  get: async (annotationId: string): Promise<Annotation> => {
    const response = await apiClient.get(`/annotations/${annotationId}`)
    return response.data
  },

  // 更新标注
  update: async (annotationId: string, data: Partial<AnnotationCreate>): Promise<Annotation> => {
    const response = await apiClient.put(`/annotations/${annotationId}`, data)
    return response.data
  },

  // 删除标注
  delete: async (annotationId: string): Promise<void> => {
    await apiClient.delete(`/annotations/${annotationId}`)
  },

  // 列出标注
  list: async (params: {
    file_path?: string
    status?: string
    annotation_type?: string
    page?: number
    page_size?: number
  }): Promise<AnnotationListResponse> => {
    const response = await apiClient.get('/annotations/list', { params })
    return response.data
  },

  // 获取统计
  getStats: async (scope: string = 'all', filePath?: string): Promise<AnnotationStats> => {
    const response = await apiClient.get('/annotations/stats', {
      params: { scope, file_path: filePath },
    })
    return response.data
  },

  // 导出标注
  export: async (format: string = 'json', scope: string = 'all', filePath?: string): Promise<string> => {
    const response = await apiClient.post('/annotations/export', {
      format,
      scope,
      file_path: filePath,
    })
    return response.data.data
  },

  // 获取标注类型
  getTypes: async (): Promise<any[]> => {
    const response = await apiClient.get('/annotations/types')
    return response.data.types
  },

  // 获取标注状态
  getStatuses: async (): Promise<any[]> => {
    const response = await apiClient.get('/annotations/statuses')
    return response.data.statuses
  },
}