import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
import './styles/index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60 * 5,  // cache data for 5 minutes
      refetchOnWindowFocus: false, // do not refetch every time user switches tabs
    }
  }
})

document.documentElement.classList.add('dark')

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <App />
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#161b27',
                color: '#f1f5f9',
                border: '1px solid #1e2535',
                borderRadius: '10px',
                fontSize: '14px',
                fontFamily: 'Sora, sans-serif',
              },
              success: {
                iconTheme: { primary: '#10b981', secondary: '#161b27' },
              },
              error: {
                iconTheme: { primary: '#ef4444', secondary: '#161b27' },
              },
            }}
          />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)