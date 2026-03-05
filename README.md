# 🧠 Knowledge Synthesizer: AI-Powered Learning Pipeline

![Application Interface](knowledge_synthesizer_ui.png)

An intelligent audio-to-knowledge system that transforms passive listening into active, retained expertise.

## 🚀 The Core Problem & AI Solution
![The Problem](problem.png)
![The AI Solution](solution.png)
![The Benefit](benefit.png)

## 👥 Who This Is For
- **EdTech Startups**: Organizations building the next generation of AI-driven adaptive learning tools.
- **Corporate Training Platforms**: Implementing internal Knowledge Management Systems (LMS) with automated summarization.
- **Content Creators & Educators**: Seeking to turn raw video/audio content into structured study materials (Flashcards, Quizzes) instantly.

## ✨ Technical Features
- **Smart Transcription**: Seamlessly converts speech to text using `SpeechRecognition` and `pydub`.
- **NLP Insights**: Automatically extracts key arguments and builds **Concept Maps** via TextBlob.
- **Active Recall Engine**: Generates automated study aids to bridge the gap between "Information" and "Retention".
- **High-Performance API**: Built with FastAPI for rapid, asynchronous processing.

## 🛠️ Backend Architect & NLP Features
The "Knowledge Synthesizer" isn't just a UI—it's a sophisticated data pipeline capable of handling high-concurrency requests.
- **Asynchronous Processing**: Leverages FastAPI’s `async` capabilities to handle audio stream processing and NLP heavy-lifting without blocking the main event loop.
- **NLP Sentiment & Polarity Analysis**: Uses TextBlob to determine the tonality of transcribed content, which aids in classifying the nature of the "knowledge" (e.g., factual vs. opinionated).
- **Automated Summarization Logic**: The backend logic parses raw transcripts to extract noun phrases and key concepts, which are then used to auto-populate study aids.
- **Extensible Audio Pipeline**: The modular design allows for easy integration with OpenAI's Whisper or Google's Speech-to-Text for enterprise-grade deployments.

## 🛠️ Tech Stack
- **Backend**: Python, [FastAPI](https://fastapi.tiangolo.com/)
- **Audio Processing**: `speech_recognition`, `pydub` (FFmpeg backend)
- **NLP Processing**: `textblob`

## 🚀 Execution & Local Demo
```bash
git clone https://github.com/amanamarjit243222/Knowledge-Synthesizer.git
cd Knowledge-Synthesizer
pip install fastapi uvicorn textblob SpeechRecognition pydub
uvicorn main:app --reload
```
*Open `index.html` in your browser to start synthesizing.*

## 📸 Application Interface
![UI Interface](knowledge_synthesizer_ui.png)

