import apiClient from './api'

export interface FileInfo {
  name: string
  type: 'file' | 'directory'
  path: string
  size?: number
  modified?: string
  file_count?: number
  is_readable: boolean
}

export interface FileBrowseResponse {
  path: string
  items: FileInfo[]
  parent?: string
  total_items: number
}

export interface FilePreviewResponse {
  path: string
  content: string
  total_lines: number
  encoding: string
}

export const fileApi = {
  // 浏览目录
  browse: async (path: string): Promise<FileBrowseResponse> => {
    const response = await apiClient.get('/files/browse', { params: { path } })
    return response.data
  },

  // 预览文件
  preview: async (filePath: string, lines?: number): Promise<FilePreviewResponse> => {
    const response = await apiClient.get('/files/preview', {
      params: { file_path: filePath, lines },
    })
    return response.data
  },

  // 搜索文件
  search: async (query: string, scope: string = 'all'): Promise<FileInfo[]> => {
    const response = await apiClient.get('/files/search', {
      params: { query, scope },
    })
    return response.data.results
  },

  // 匹配文件
  match: async (ocrFile: string): Promise<any[]> => {
    const response = await apiClient.post('/files/match', { ocr_file: ocrFile })
    return response.data.recommended_files
  },

  // 获取文件树
  getTree: async (): Promise<any> => {
    const response = await apiClient.get('/files/tree')
    return response.data
  },

  // 获取基础路径
  getBasePaths: async (): Promise<any> => {
    const response = await apiClient.get('/files/base-paths')
    return response.data
  },
}