# Browser-Based Media Upload Instructions

This document provides instructions for uploading media and submitting perception questions through a web interface.

## Quick Start

### Using curl with Form Upload

The simplest way to test browser-style uploads is with curl's form mode:

```bash
curl -X POST http://localhost:8002/media/upload \
  -H "Authorization: Bearer your-token-here" \
  -F "file=@image.jpg" \
  -F 'metadata={"source":"browser","user":"test-user"}'
```

### Using Python Requests

```python
import requests

url = "http://localhost:8002/media/upload"
token = "your-token-here"

headers = {
    "Authorization": f"Bearer {token}"
}

files = {
    "file": ("image.jpg", open("image.jpg", "rb"), "image/jpeg")
}

data = {
    "metadata": '{"source": "browser", "user": "demo-user"}'
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

### Using JavaScript (Fetch API)

```html
<!DOCTYPE html>
<html>
<head>
    <title>LOGOS Media Upload</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .upload-container {
            border: 2px dashed #ccc;
            padding: 40px;
            text-align: center;
            border-radius: 8px;
        }
        .button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        .button:hover {
            background-color: #0056b3;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        input[type="file"] {
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>LOGOS Media Ingestion</h1>
    
    <div class="upload-container">
        <h2>Upload Media File</h2>
        <input type="file" id="fileInput" accept="image/*,video/*,audio/*">
        <br>
        <input type="text" id="tokenInput" placeholder="Enter authentication token" 
               style="width: 100%; padding: 8px; margin: 10px 0;">
        <br>
        <button class="button" onclick="uploadFile()">Upload</button>
    </div>
    
    <div id="result" class="result" style="display: none;">
        <h3>Upload Result</h3>
        <pre id="resultContent"></pre>
    </div>

    <script>
        const API_BASE = "http://localhost:8002";
        
        async function uploadFile() {
            const fileInput = document.getElementById("fileInput");
            const tokenInput = document.getElementById("tokenInput");
            const resultDiv = document.getElementById("result");
            const resultContent = document.getElementById("resultContent");
            
            if (!fileInput.files.length) {
                alert("Please select a file");
                return;
            }
            
            const token = tokenInput.value || "default-token-12345678";
            const file = fileInput.files[0];
            
            // Create FormData
            const formData = new FormData();
            formData.append("file", file);
            formData.append("metadata", JSON.stringify({
                source: "browser",
                filename: file.name,
                size: file.size,
                type: file.type
            }));
            
            try {
                // Show uploading state
                resultDiv.style.display = "block";
                resultContent.textContent = "Uploading...";
                
                // Upload file
                const response = await fetch(`${API_BASE}/media/upload`, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    },
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultContent.textContent = JSON.stringify(data, null, 2);
                    
                    // Optionally trigger simulation
                    if (confirm("Upload successful! Would you like to run a simulation?")) {
                        await runSimulation(data.media_id, token);
                    }
                } else {
                    resultContent.textContent = `Error: ${JSON.stringify(data, null, 2)}`;
                }
            } catch (error) {
                resultContent.textContent = `Error: ${error.message}`;
            }
        }
        
        async function runSimulation(mediaId, token) {
            const resultContent = document.getElementById("resultContent");
            
            try {
                resultContent.textContent = "Running simulation...";
                
                const response = await fetch("http://localhost:8000/sophia/simulate", {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        capability_id: "browser-upload-simulation",
                        context: {
                            perception_sample_id: mediaId,
                            source: "browser"
                        },
                        k_steps: 5
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultContent.textContent = 
                        "Simulation started!\n\n" + 
                        JSON.stringify(data, null, 2);
                } else {
                    resultContent.textContent = 
                        "Upload succeeded but simulation failed:\n\n" + 
                        JSON.stringify(data, null, 2);
                }
            } catch (error) {
                resultContent.textContent = 
                    "Upload succeeded but simulation request failed:\n\n" + 
                    error.message;
            }
        }
    </script>
</body>
</html>
```

Save this as `upload.html` and open it in a browser. Make sure the media ingestion service is running first.

## Integration with Apollo Browser UI

When Apollo browser UI is available, the media upload will be integrated as follows:

### 1. Perception Tab

The Apollo browser will have a dedicated "Perception" tab with:

- **Upload Panel**: Drag-and-drop interface for uploading media
- **Stream Panel**: Controls for starting/stopping WebRTC streams
- **Questions Panel**: Form for submitting perception questions
- **Results Panel**: Visualization of simulation results

### 2. Upload Workflow

```typescript
// TypeScript/React component example
import { useState } from 'react';
import { useMediaUpload } from '@logos/sdk';

function PerceptionUploader() {
  const [file, setFile] = useState<File | null>(null);
  const { upload, isUploading, error } = useMediaUpload();
  
  const handleUpload = async () => {
    if (!file) return;
    
    const result = await upload(file, {
      source: 'apollo-browser',
      timestamp: new Date().toISOString()
    });
    
    console.log('Uploaded:', result.media_id);
  };
  
  return (
    <div>
      <input 
        type="file" 
        onChange={e => setFile(e.target.files?.[0] || null)} 
      />
      <button onClick={handleUpload} disabled={isUploading}>
        {isUploading ? 'Uploading...' : 'Upload'}
      </button>
      {error && <div>Error: {error.message}</div>}
    </div>
  );
}
```

### 3. Perception Question Workflow

```typescript
// Combined upload + simulation
async function submitPerceptionQuestion(
  file: File, 
  question: string
): Promise<SimulationResult> {
  // 1. Upload media
  const upload = await mediaClient.upload(file);
  
  // 2. Trigger simulation
  const simulation = await sophiaClient.simulate({
    capability_id: 'perception-question',
    context: {
      perception_sample_id: upload.media_id,
      question: question
    },
    k_steps: 10
  });
  
  // 3. Poll for results
  const results = await sophiaClient.getSimulation(simulation.process_uuid);
  
  return results;
}

// Usage in UI
const result = await submitPerceptionQuestion(
  imageFile,
  "Will the robot successfully pick up the red block?"
);

// Display result with confidence visualization
<SimulationViewer 
  process={result.process}
  states={result.states}
  confidence={result.states[result.states.length - 1].confidence}
/>
```

## WebRTC Stream Setup

For real-time perception from webcam:

### Browser JavaScript

```javascript
// Start webcam stream
async function startWebcamStream() {
    const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
    });
    
    const video = document.createElement('video');
    video.srcObject = stream;
    video.play();
    
    // Capture frames at 5 FPS
    const canvas = document.createElement('canvas');
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext('2d');
    
    const frameInterval = setInterval(async () => {
        // Draw current frame to canvas
        ctx.drawImage(video, 0, 0, 640, 480);
        
        // Convert to blob
        const blob = await new Promise(resolve => 
            canvas.toBlob(resolve, 'image/jpeg', 0.8)
        );
        
        // Upload frame
        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');
        formData.append('metadata', JSON.stringify({
            source: 'webcam',
            timestamp: new Date().toISOString()
        }));
        
        await fetch('http://localhost:8002/media/upload', {
            method: 'POST',
            headers: { 'Authorization': 'Bearer your-token' },
            body: formData
        });
    }, 200); // 5 FPS
    
    // Stop after 30 seconds
    setTimeout(() => {
        clearInterval(frameInterval);
        stream.getTracks().forEach(track => track.stop());
    }, 30000);
}
```

## CORS Configuration

For browser-based uploads, ensure CORS is configured:

```python
# Already configured in logos_perception/app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Apollo URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, restrict origins to your deployed Apollo domain.

## Authentication Token Management

### Client-Side Token Storage

```javascript
// Store token in localStorage
localStorage.setItem('logos_token', 'your-token-here');

// Retrieve for API calls
const token = localStorage.getItem('logos_token');

// Clear on logout
localStorage.removeItem('logos_token');
```

### Token Refresh Pattern

```javascript
class LogosClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.token = token;
    }
    
    async fetch(endpoint, options = {}) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${this.token}`
            }
        });
        
        if (response.status === 401) {
            // Token expired, refresh or re-authenticate
            await this.refreshToken();
            return this.fetch(endpoint, options);
        }
        
        return response;
    }
    
    async refreshToken() {
        // Implement token refresh logic
    }
}
```

## Example: Complete Browser Upload Flow

```html
<!DOCTYPE html>
<html>
<head>
    <title>Perception Question Demo</title>
</head>
<body>
    <h1>Ask a Perception Question</h1>
    
    <input type="file" id="image" accept="image/*">
    <br><br>
    
    <input type="text" id="question" placeholder="Enter your question" 
           style="width: 400px;">
    <br><br>
    
    <button onclick="submitQuestion()">Submit Question</button>
    
    <div id="status"></div>
    <div id="result"></div>

    <script>
        const TOKEN = "your-token-12345678";
        
        async function submitQuestion() {
            const file = document.getElementById('image').files[0];
            const question = document.getElementById('question').value;
            const statusDiv = document.getElementById('status');
            const resultDiv = document.getElementById('result');
            
            if (!file || !question) {
                alert('Please select an image and enter a question');
                return;
            }
            
            // Step 1: Upload image
            statusDiv.innerHTML = 'Uploading image...';
            const formData = new FormData();
            formData.append('file', file);
            formData.append('metadata', JSON.stringify({ question }));
            
            const uploadResp = await fetch('http://localhost:8002/media/upload', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${TOKEN}` },
                body: formData
            });
            
            const uploadData = await uploadResp.json();
            
            // Step 2: Trigger simulation
            statusDiv.innerHTML = 'Running simulation...';
            const simResp = await fetch('http://localhost:8000/sophia/simulate', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${TOKEN}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    capability_id: 'perception-question',
                    context: {
                        perception_sample_id: uploadData.media_id,
                        question: question
                    },
                    k_steps: 5
                })
            });
            
            const simData = await simResp.json();
            
            statusDiv.innerHTML = 'Simulation complete!';
            resultDiv.innerHTML = `
                <h2>Results</h2>
                <p><strong>Process UUID:</strong> ${simData.process_uuid}</p>
                <p><strong>States Generated:</strong> ${simData.states_count}</p>
                <p><strong>Model Version:</strong> ${simData.model_version}</p>
            `;
        }
    </script>
</body>
</html>
```

## Next Steps

- See `MEDIA_INGESTION_CLI.md` for command-line usage
- See `docs/phase2/VERIFY.md` for verification procedures
- See Apollo browser documentation (when available) for full UI integration
