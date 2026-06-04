import axios from 'axios'

const API_BASE = window.__PAPERMAKER_API__ || window.location.origin

export const api = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── 请求拦截器 ──
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error),
)

// ── 响应拦截器 ──
api.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body.code !== undefined && body.code !== 0) {
      console.warn(`[API] ${body.message || 'unknown error'}`)
    }
    return body
  },
  (error) => {
    console.error(`[API] request failed:`, error.message)
    return Promise.reject(error)
  },
)

export interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
}
