# 🧠 Knowledge Synthesizer

An intelligent audio-to-knowledge pipeline that transcribes lectures/meetings and automatically generates study materials like flashcards, quizzes, and concept maps.

## ✨ Features
- **Smart Transcription:** Converts audio files and raw text into structured data using SpeechRecognition and AudioSegment.
- **Automated Processing:**
  - Extracts key arguments and generates automated summaries using TextBlob.
  - Generates Active Recall Quizzes and Spaced Repetition flashcards.
  - Automatically identifies core concepts to build relationships in a Knowledge Graph.
- **FastAPI Backend:** A robust, high-performance API supporting file uploads and immediate linguistic analysis.

## 🛠️ Tech Stack
- **Backend:** Python, [FastAPI](https://fastapi.tiangolo.com/)
- **Audio Processing:** `speech_recognition`, `pydub` (requires FFmpeg)
- **NLP:** `textblob`
- **Frontend:** HTML, JavaScript

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- [FFmpeg](https://ffmpeg.org/download.html) installed and added to your system PATH for audio processing.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/amanamarjit243222/Knowledge-Synthesizer.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Knowledge-Synthesizer
   ```
3. Install the required Python packages:
   ```bash
   pip install fastapi uvicorn textblob SpeechRecognition pydub python-multipart
   ```
   *(Note: You may need to run `python -m textblob.download_corpora` if TextBlob requires it)*

4. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```
5. Open `index.html` in your browser to use the client interface.

## 📸 Demo
![Knowledge Synthesizer Interface](knowledge_synthesizer_ui.png)

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📄 License
This project is open-source.
