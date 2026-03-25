import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import router from './router'
import ErrorBoundary from './ErrorBoundary'
import './index.css'

// 配置 Ant Design 主题
const theme = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
  },
};

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <ConfigProvider locale={zhCN} theme={theme}>
        <RouterProvider router={router} />
      </ConfigProvider>
    </ErrorBoundary>
  </StrictMode>,
)
