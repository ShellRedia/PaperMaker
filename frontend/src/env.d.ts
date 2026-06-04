/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface Window {
  __PAPERMAKER_API__?: string
  pywebview?: {
    api: {
      open_file_dialog: () => Promise<string>
      get_app_data_path: () => Promise<string>
    }
  }
}
