import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Chat from './pages/Chat'
import Home from './pages/Home'
import AIInterface from './pages/AIInterface'
import ErrorBoundary from './components/common/ErrorBoundary'
import { WebSocketProvider } from './providers/WebSocketProvider'

function App() {
  return (
    <ErrorBoundary>
      <WebSocketProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/ai" element={<AIInterface />} />
          </Routes>
        </Layout>
      </WebSocketProvider>
    </ErrorBoundary>
  )
}

export default App