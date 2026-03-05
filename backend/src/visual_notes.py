import os
import shutil
from datetime import datetime

# Try to import Pillow for image processing
try:
    from PIL import Image
except ImportError:
    Image = None
    print("WARNING: 'Pillow' library not found. Install with 'pip install Pillow' for image support.")

# Try to import pytesseract for OCR (Reading text from images)
try:
    import pytesseract
except ImportError:
    pytesseract = None

class VisualNoteManager:
    """
    Handles multi-modal input: Saving whiteboard photos and 
    embedding them into the session context.
    """
    
    def __init__(self, storage_dir="static_visuals"):
        # Create a folder to store the images
        self.storage_dir = storage_dir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def save_and_process(self, temp_file_path: str, original_filename: str, timestamp_str: str = "00:00") -> dict:
        """
        Saves the image, runs OCR (if available), and returns data to embed in the transcript.
        """
        # 1. Generate a safe, unique filename
        # Use timestamp to prevent overwrites
        safe_name = f"{int(datetime.now().timestamp())}_{original_filename.replace(' ', '_')}"
        target_path = os.path.join(self.storage_dir, safe_name)
        
        # 2. Move file from temp location to storage folder
        shutil.move(temp_file_path, target_path)
        
        # 3. Perform OCR (Optical Character Recognition)
        ocr_text = ""
        if Image and pytesseract:
            try:
                # Basic check for Tesseract binary in common Windows paths
                # (Users often forget to add it to PATH, similar to FFmpeg)
                tesseract_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
                ]
                
                # If tesseract is not in PATH, try to find it manually
                if shutil.which("tesseract") is None:
                    for p in tesseract_paths:
                        if os.path.exists(p):
                            pytesseract.pytesseract.tesseract_cmd = p
                            break

                img = Image.open(target_path)
                ocr_text = pytesseract.image_to_string(img)
                
                # Clean up text (remove excessive newlines)
                ocr_text = " ".join(ocr_text.split()).strip()
            except Exception as e:
                ocr_text = "[Text extraction failed or Tesseract not installed]"
        else:
            if not Image:
                ocr_text = "[OCR Unavailable - 'Pillow' library missing]"
            elif not pytesseract:
                ocr_text = "[OCR Unavailable - 'pytesseract' library missing]"

        # 4. Generate Embed Data
        # This matches the URL path we will mount in main.py
        public_url = f"/visuals/{safe_name}"
        
        return {
            "file_path": target_path,
            "public_url": public_url,
            "timestamp": timestamp_str,
            "ocr_text": ocr_text,
            # This tag can be appended to your transcript text
            "embed_tag": f"\n\n[VISUAL NOTE @ {timestamp_str}]\n![Whiteboard Snapshot]({public_url})\n> *Detected Text: {ocr_text[:150]}...*\n"
        }
