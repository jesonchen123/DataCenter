import { Routes, Route } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { Dashboard } from './pages/Dashboard'
import { DocImport } from './pages/DocImport'
import { ProcessTasks } from './pages/ProcessTasks'
import { ReviewCenter } from './pages/ReviewCenter'
import { KnowledgeBase } from './pages/KnowledgeBase'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/import" element={<DocImport />} />
        <Route path="/tasks" element={<ProcessTasks />} />
        <Route path="/review" element={<ReviewCenter />} />
        <Route path="/knowledge" element={<KnowledgeBase />} />
      </Route>
    </Routes>
  )
}
