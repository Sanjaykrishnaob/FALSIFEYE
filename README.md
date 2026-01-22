# FALSIFEYE - AI-Powered Digital Forensic Platform

FALSIFEYE is a comprehensive digital forensic tool designed to assist legal professionals, law enforcement, and forensic analysts in verifying the authenticity of digital evidence. It leverages advanced AI and signal processing techniques to detect deepfakes, manipulated documents, and synthetic audio.

## Key Features

### 1. Multimedia Forensics
*   **Image Analysis**: Uses **Error Level Analysis (ELA)** to detect spliced or modified regions in images.
*   **Video Verification**: Analyzes frames using **FFT (Fast Fourier Transform)** and **Optical Flow** to detect deepfake artifacts and unnatural motion.
*   **Audio Forensics**: Checks for **Voice Variance** and spectral anomalies to identify synthesized or robotic speech (TTS).

### 2. Document Analysis
*   **PDF Forensics**: Scans document metadata and internal structure to detect traces of editing software (e.g., Photoshop, PDF Editors) vs. legitimate scanners.
*   **Security Check**: Detects embedded JavaScript or suspicious scripts within documents.

### 3. AI-Powered Transcription
*   **OpenAI Whisper Integration**: Automatically transcribes audio and video evidence with high accuracy.
*   **Multilingual Support**: Capable of handling various languages and accents.

### 4. Expert Forensic Chatbot
*   **AI Assistant**: A RAG (Retrieval-Augmented Generation) chatbot powered by **SentenceTransformers**.
*   **Context-Aware**: Can explain specific analysis results (e.g., "What does a high ELA score mean?") and general forensic concepts.

### 5. Legal Reporting
*   **Automated PDF Reports**: Generates professional forensic reports with:
    *   Authenticity Scores (0-100)
    *   Detailed Anomaly Logs
    *   Digital Fingerprints (SHA-256 Hash)
    *   Chain of Custody Information

## Installation and Setup

### Prerequisites
*   **Python 3.10+**
*   **FFmpeg**: Required for audio/video processing. Ensure it is installed and added to your system PATH.

### Installation Steps
1.  **Clone/Download** the repository.
2.  **Install Dependencies**:
    ```bash
    pip install -r falsifeye/requirements.txt
    ```
    *Note: This will install PyTorch, OpenCV, Librosa, SentenceTransformers, and OpenAI Whisper.*

## Execution Instructions

### Option 1: Automated Start (Windows)
Execute the **`run_server.bat`** file located in the root directory.

### Option 2: Manual Start
Open a terminal in the project root and run:
```bash
python falsifeye/app.py
```

### Accessing the Dashboard
Once the server is running, open a web browser and navigate to:
**http://localhost:8081**

## Project Structure

*   **`falsifeye/app.py`**: Main Flask application server.
*   **`falsifeye/modules/`**: Core forensic logic.
    *   `media_verifier.py`: Image, Video, Audio, and Document analysis algorithms.
    *   `chatbot.py`: AI Chatbot logic using Semantic Search.
    *   `transcriber.py`: Whisper AI integration.
    *   `report_generator.py`: PDF report creation.
*   **`falsifeye/templates/`**: HTML frontend files.
*   **`uploads/`**: Temporary storage for analyzed evidence.

## Cloud Deployment (Render)

### Prerequisites
*   **GitHub Account** (to host the repository)
*   **Render Account** (https://render.com — free tier available)

### Deploy Steps

1. **Initialize Git & Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: FALSIFEYE with Render deployment config"
   git remote add origin https://github.com/YOUR_USERNAME/falsifeye.git
   git branch -M main
   git push -u origin main
   ```

2. **Connect to Render:**
   - Visit https://dashboard.render.com
   - Click **New → Web Service**
   - Select **Build and deploy from a Git repository**
   - Paste your GitHub repo URL
   - Render will auto-detect `render.yaml` and deploy
   - Build logs visible in the dashboard (~5-10 minutes for first build)

3. **Access Live App:**
   - Once deployed, your app is live at `https://<service-name>.onrender.com`
   - The service will restart automatically if it crashes
   - Default free tier: 512 MB RAM, shared CPU (sufficient for demos)

### Monitor & Manage (Render Dashboard)
*   View logs, restart service, update environment variables
*   Automatic deploys trigger on every `git push` to `main`

### Troubleshooting Deployment
*   **Build fails:** Check build logs in Render dashboard; ensure all dependencies in `falsifeye/requirements.txt` are compatible
*   **App crashes on startup:** Check runtime logs; likely missing `ffmpeg` or module import errors
*   **Slow first request:** Render free tier sleeps services after 15 min inactivity; first request wakes it (~30s)

## Troubleshooting

*   **Server Startup Issues:**
    *   Check `server_err.log` for detailed error messages.
    *   Ensure no other service is using port **8081**.
*   **Whisper/FFmpeg Errors:**
    *   Ensure `ffmpeg` is installed correctly and accessible via the command line.
    *   The first execution requires internet access to download the Whisper model (~140MB).
*   **Chatbot Latency:**
    *   The chatbot runs on the CPU to ensure stability. Allow a few seconds for initialization during the first query.

---
*Developed for the Forensic Initiative - Dec 2025*  
*Deployment: Docker (Render) + GitHub Actions*
