import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import MainLayout from './components/Layout/MainLayout'
import HomePage from './pages/HomePage'
import ComparePage from './pages/ComparePage'
import AnnotationPage from './pages/AnnotationPage'
import StatsPage from './pages/StatsPage'

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/annotations" element={<AnnotationPage />} />
          <Route path="/stats" element={<StatsPage />} />
        </Routes>
      </MainLayout>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </Router>
  )
}

export default App