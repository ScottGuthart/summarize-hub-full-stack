import { useState, useEffect } from 'react'

const TaskProgress = ({ task, onReset }) => {
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('')
  const [message, setMessage] = useState('')
  const [isComplete, setIsComplete] = useState(false)
  const [isSuccessful, setIsSuccessful] = useState(false)

  const handleDownload = async () => {
    try {
      const response = await fetch(`/api/task/${task.id}/download`)
      if (!response.ok) {
        throw new Error('Download failed')
      }
      
      // Get the filename from the Content-Disposition header if present
      const contentDisposition = response.headers.get('Content-Disposition')
      let filename = 'download'
      if (contentDisposition) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition)
        if (matches != null && matches[1]) {
          filename = matches[1].replace(/['"]/g, '')
        }
      }
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Download error:', error)
      setStatus('Download failed: ' + error.message)
    }
  }

  useEffect(() => {
    let pollInterval

    const pollTask = async () => {
      if (!task) return

      try {
        const response = await fetch(`/api/task/${task.id}`)
        if (!response.ok) {
          throw new Error(`Failed to fetch task status: ${response.status}`)
        }
        
        const taskData = await response.json()
        console.log('Task data:', taskData)
        
        if (taskData.complete) {
          clearInterval(pollInterval)
          setProgress(100)
          setIsComplete(true)
          setIsSuccessful(taskData.succeeded !== false)
          setStatus(taskData.succeeded ? 'Processing complete!' : 'Processing failed')
        } else {
          setProgress(taskData.progress || 0)
          setStatus(`Processing: ${taskData.progress || 0}%`)
          setMessage(taskData.progress_message || '')
        }
      } catch (error) {
        console.error('Error polling task:', error)
        setStatus(`Error checking progress: ${error.message}`)
        clearInterval(pollInterval)
      }
    }

    if (task) {
      // Start polling every 5 seconds
      pollInterval = setInterval(pollTask, 5000)
      // Poll immediately
      pollTask()
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
    }
  }, [task])

  if (!task) return null

  return (
    <div className="progress-container">
      <div className="progress-bar">
        <div 
          className="progress-fill"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="status-message">{status}</p>
      {message && <p className="progress-message">{message}</p>}
      <div className="button-container">
        {isComplete && isSuccessful && (
          <button onClick={handleDownload} className="download-button">
            Download Result
          </button>
        )}
        <button onClick={onReset} className="reset-button">
          Upload Another File
        </button>
      </div>
    </div>
  )
}

export default TaskProgress 