/**
 * API 配置
 *
 * 所有地址与密钥都来自构建期环境变量（.env / .env.local）。
 * 注意：只有 VITE_ 前缀的变量会被注入前端，且会以明文内联进打包产物，
 * 因此 VITE_AI_API_KEY 只适合本地演示，不要用于公开部署。
 */

// 末尾斜杠统一去掉，避免拼出 //api/xxx
const rawBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export const apiConfig = {
  baseURL: rawBaseURL.replace(/\/+$/, ''),
}

export const aiChatConfig = {
  // OpenAI 兼容接口（默认阿里云百炼 DashScope）
  apiEndpoint:
    import.meta.env.VITE_AI_ENDPOINT ||
    'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',

  apiKey: (import.meta.env.VITE_AI_API_KEY || '').trim(),

  model: import.meta.env.VITE_AI_MODEL || 'qwen3-max-preview',
}

const PLACEHOLDERS = ['', 'sk-xxx', 'your-api-key-here', 'change-me']

/** AI 问答是否已配置可用 */
export const isAiConfigured = () => !PLACEHOLDERS.includes(aiChatConfig.apiKey)
