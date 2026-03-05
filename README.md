# 🧠 Knowledge Synthesizer: AI-Powered Learning Pipeline

An intelligent audio-to-knowledge system that transforms passive listening into active learning materials.

## 🚀 The Use Case: Bridging the Learning Gap
Traditional lectures and meetings are often lost to time. **Knowledge Synthesizer** bridges this gap by automatically transcribing audio and distilling it into structured memory aids. It is designed for students and professionals who need to move from "information" to "long-term retention" in minutes, not hours.

## 📈 The Pipeline (Visual)
![The Problem](problem.png)
![The AI Solution](solution.png)
![The Benefit](benefit.png)

## ✨ Features
- **Smart Transcription**: Seamlessly converts speech to text using `SpeechRecognition`.
- **NLP Insights**: Automatically extracts key arguments and builds **Concept Maps**.
- **Active Recall Engine**: Generates quizzes and flashcards to power your study sessions.
- **RESTful Architecture**: High-performance FastAPI backend for rapid processing.

## 📸 Application Layout
![UI Interface](knowledge_synthesizer_ui.png)

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python)
- **Audio Logic**: `pydub`, `SpeechRecognition` (via FFmpeg)
- **NLP Engine**: `textblob`
- **Frontend**: HTML5/Vanilla JS

## 🚀 Execution
```bash
pip install fastapi uvicorn textblob SpeechRecognition pydub
uvicorn main:app --reload
```
Open `index.html` to begin synthesizing.

## 📄 License
Open-source.
