import os
import random
from typing import List
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr

class AudioDiarizer:
    """
    A lightweight diarization tool that splits audio on silence and 
    assigns speaker labels (heuristic-based for demo purposes).
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def process_audio(self, file_path: str) -> str:
        """
        Splits audio into chunks based on silence, transcribes them,
        and assigns speaker labels.
        """
        try:
            # Load the audio file
            # pydub handles wav, mp3, ogg, flv, etc.
            sound = AudioSegment.from_file(file_path)
        except Exception as e:
            return f"Error loading audio file: {e}"

        # Adjust these parameters for sensitivity
        # min_silence_len: length of silence in ms to consider a split (e.g., 700ms pause)
        # silence_thresh: how quiet it must be (dBFS)
        chunks = split_on_silence(
            sound,
            min_silence_len=700,
            silence_thresh=sound.dBFS - 14,
            keep_silence=500
        )

        full_transcript = []
        
        # Simulation Logic: 
        # Since we aren't using a heavy ML model (like PyAnnotate) which requires 
        # CUDA and large downloads, we simulate "turn-taking" based on chunk splitting.
        speakers = ["Speaker A", "Speaker B"]
        current_speaker_idx = 0

        # If no silence found, process the whole file as one
        if not chunks:
            return self._transcribe_chunk(file_path, "Speaker A")

        for i, chunk in enumerate(chunks):
            # Export chunk to a temp file for the recognizer
            chunk_filename = f"temp_chunk_{i}.wav"
            chunk.export(chunk_filename, format="wav")

            # Transcribe
            text = self._transcribe_chunk_file(chunk_filename)
            
            # Cleanup temp file
            if os.path.exists(chunk_filename):
                os.remove(chunk_filename)

            if text:
                # Add to transcript
                speaker = speakers[current_speaker_idx]
                full_transcript.append(f"{speaker}: {text}")

                # Heuristic: If text is long enough, assume the next chunk might be a reply
                # This simulates conversation flow for the output
                if len(text.split()) > 5: 
                    current_speaker_idx = 1 - current_speaker_idx  # Switch speaker

        return "\n\n".join(full_transcript)

    def _transcribe_chunk_file(self, chunk_path: str) -> str:
        try:
            with sr.AudioFile(chunk_path) as source:
                audio_data = self.recognizer.record(source)
                # Use Google Web Speech API
                return self.recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return ""  # Unintelligible audio
        except sr.RequestError:
            return "[API Error]"
        except Exception:
            return ""

    def _transcribe_chunk(self, file_path: str, speaker_label: str) -> str:
        """Fallback for non-chunked audio"""
        text = self._transcribe_chunk_file(file_path)
        if text:
            return f"{speaker_label}: {text}"
        return "Audio could not be processed."
