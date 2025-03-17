import { useState } from 'react'
import './App.css'
import FileUpload from './components/FileUpload'
import TaskProgress from './components/TaskProgress'

function App() {
  const [currentTask, setCurrentTask] = useState(null)

  const handleTaskCreated = (taskData) => {
    setCurrentTask(taskData)
  }

  const handleReset = () => {
    setCurrentTask(null)
  }

  return (
    <div className="app-container">
      <h1>File Upload</h1>
      {!currentTask ? (
        <FileUpload onTaskCreated={handleTaskCreated} />
      ) : (
        <TaskProgress task={currentTask} onReset={handleReset} />
      )}
    </div>
  )
}

export default App
