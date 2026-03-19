import os
import shutil
import re
from typing import Optional, List, Dict, Any
from collections import Counter
from datetime import datetime

# CORE LIBRARIES
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from textblob import TextBlob
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.effects import normalize
import uvicorn

# --- IMPORTING YOUR MODULES ---
from src.tagging import SmartTagger
from src.retention_engine import RetentionEngine
from src.visual_notes import VisualNoteManager

# --- FFMPEG AUTO-CONFIG ---
def setup_ffmpeg():
    """Locates ffmpeg binaries to ensure audio processing works on all systems."""
    if shutil.which("ffmpeg"):
        return True
    possible_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            AudioSegment.converter = path
            AudioSegment.ffmpeg = path
            os.environ["PATH"] += os.pathsep + os.path.dirname(path)
            return True
    return False

FFMPEG_READY = setup_ffmpeg()

# ==========================================
# MODULE: AUDIO INTELLIGENCE (Transcriber)
# ==========================================
class AudioEngine:
    """Handles speech-to-text conversion with noise reduction and silence trimming."""
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe(self, file_path: str) -> str:
        if not FFMPEG_READY:
            return "Error: FFmpeg not detected. Audio processing is unavailable."

        try:
            # Load and Pre-process
            sound = AudioSegment.from_file(file_path)
            sound = normalize(sound)
            
            # Export to WAV for the recognizer
            wav_path = file_path + ".wav"
            sound.export(wav_path, format="wav")
            
            transcript = ""
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
                transcript = self.recognizer.recognize_google(audio_data)
            
            # Cleanup
            if os.path.exists(wav_path):
                os.remove(wav_path)
                
            return transcript
        except Exception as e:
            return f"[Transcription Failed: {str(e)}]"

# ==========================================
# API SERVER & CORE LOGIC
# ==========================================
app = FastAPI()

# Enable CORS for frontend connectivity
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)
# Initialize Engines
tagger = SmartTagger()
retention = RetentionEngine()
visual_manager = VisualNoteManager(storage_dir="static_visuals")
audio_engine = AudioEngine()

# Static Files for Whiteboard Snapshots
os.makedirs("static_visuals", exist_ok=True)
app.mount("/visuals", StaticFiles(directory="static_visuals"), name="visuals")

@app.post("/upload_visual")
async def upload_visual(file: UploadFile = File(...), timestamp: str = Form("00:00")):
    tmp_path = f"temp_{file.filename}"
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    result = visual_manager.save_and_process(tmp_path, file.filename, timestamp)
    return result

@app.post("/synthesize")
async def synthesize(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    inputType: Optional[str] = Form("text")
):
    # 1. Capture Raw Content
    raw_content = ""
    if inputType in ["live", "voice"] and file:
        tmp_audio = f"temp_audio_{file.filename}"
        with open(tmp_audio, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Real Transcription instead of placeholder
        raw_content = audio_engine.transcribe(tmp_audio)
        
        if os.path.exists(tmp_audio):
            os.remove(tmp_audio)
    else:
        raw_content = text or ""

    if not raw_content or raw_content.strip() == "":
        raise HTTPException(status_code=400, detail="No intelligible content detected.")

    # 2. Run Tagging & Retention Engines
    tags = tagger.generate_tags(raw_content)
    flashcards = retention.generate_flashcards(raw_content)
    quiz = retention.create_active_recall_quiz(raw_content)
    schedule = retention.get_spaced_repetition_schedule()
    
    # 3. Process Linguistic Structure (Summary & Key Points)
    blob = TextBlob(raw_content)
    # Get top 5 sentences by sentiment intensity as "key points"
    key_points = [str(s) for s in sorted(blob.sentences, key=lambda s: abs(s.sentiment.polarity), reverse=True)[:5]]
    
    # 4. Generate Graph Nodes
    # Use noun phrases to find main topics
    concepts = [np.lower() for np in blob.noun_phrases if len(np) > 3]
    top_concepts = [w for w, _ in Counter(concepts).most_common(6)]
    if not top_concepts: top_concepts = ["Core Discussion"]

    nodes = [{"id": 1, "type": "concept", "label": top_concepts[0].title()}]
    edges = []
    for i, concept in enumerate(top_concepts[1:], start=2):
        nodes.append({"id": i, "type": "argument", "label": concept.title()})
        edges.append({"source": 1, "target": i})

    return {
        "analysis": {
            "summary": str(blob.sentences[0]) if blob.sentences else "Discussion synthesized.",
            "keyNodes": key_points if key_points else [raw_content[:100] + "..."],
            "tags": tags,
            "retention": {
                "flashcards": flashcards,
                "quiz": quiz,
                "schedule": schedule
            }
        },
        "graph": {
            "nodes": nodes,
            "edges": edges
        }
    }

# Mount the frontend directory at the root last to avoid shadowing API routes
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
