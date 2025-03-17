import { useState } from 'react'

const FileUpload = ({ onTaskCreated }) => {
  const [file, setFile] = useState(null)
  const [uploadStatus, setUploadStatus] = useState('')

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0]
    setFile(selectedFile)
    setUploadStatus('')
  }

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus('Please select a file first')
      return
    }

    setUploadStatus('Uploading...')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.messages?.form?.file?.[0] || `Upload failed with status: ${response.status}`;
        throw new Error(errorMessage);
      }

      const taskData = await response.json()
      onTaskCreated(taskData)
    } catch (error) {
      console.error('Upload error:', error)
      setUploadStatus(`Upload failed: ${error.message}`)
    }
  }

  return (
    <div className="upload-container">
      <input
        type="file"
        onChange={handleFileChange}
        accept=".xlsx,.xls,.csv"
        className="file-input"
      />
      <button
        onClick={handleUpload}
        disabled={!file}
        className="upload-button"
      >
        Upload File
      </button>

      {file && (
        <div className="file-info">
          <p>Selected file: {file.name}</p>
          <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
        </div>
      )}

      {uploadStatus && (
        <p className="status-message">{uploadStatus}</p>
      )}
    </div>
  )
}

export default FileUpload 