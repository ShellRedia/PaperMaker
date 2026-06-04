import { api } from '../api'

export interface LLMConfig {
  api_url: string
  api_key: string
  model_name: string
}

export interface TokenUsage {
  prompt_tokens?: number
  completion_tokens?: number
  total_tokens?: number
}

export interface TranslateResult {
  english: string
  chinese: string
  usage?: TokenUsage
}

export const settingsApi = {
  /** 获取 LLM 配置 */
  async getLLMConfig(): Promise<LLMConfig> {
    const res = await api.get('/settings/llm-config')
    return res.data as LLMConfig
  },

  /** 更新 LLM 配置 */
  async updateLLMConfig(config: LLMConfig): Promise<void> {
    await api.put('/settings/llm-config', config)
  },
}
