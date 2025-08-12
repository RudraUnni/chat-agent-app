import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Chat from './pages/Chat'
import Home from './pages/Home'
import ErrorBoundary from './components/common/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </Layout>
    </ErrorBoundary>
  )
}

export default App