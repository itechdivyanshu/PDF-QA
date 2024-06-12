// App.js (React.js Frontend)

import React, { useState } from 'react';
import ChatApp from './ChatApp';
import axios from 'axios';
import './App.css'; // Import CSS file for styling

function App() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [documentId, setDocumentId] = useState(null);

  // Function to handle file upload
  const handleFileUpload = (event) => {
    setFile(event.target.files[0]);
  };

  // Function to handle file submission
  const handleSubmitFile = async () => {
    if (!file) {
      setUploadStatus('Please select a file first.');
      return;
    }
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post('http://localhost:8000/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setDocumentId(response.data.id);
      setUploadStatus(`Uploaded successfully: ${response.data.filename}`);
    } catch (error) {
      console.error('Error:', error);
      setUploadStatus('Upload failed');
    }
  };

  return (
    <div>
      <h1>PDF Document QA System</h1>
      {!documentId ? (
        <>
          <div className="upload">
            <input type="file" onChange={handleFileUpload} />
            <button onClick={handleSubmitFile}>Upload & Process</button>
            <p>{uploadStatus}</p>
          </div>
        </>
      ) : (
        <ChatApp documentId={documentId} />
      )}
    </div>
  );
}

export default App;
