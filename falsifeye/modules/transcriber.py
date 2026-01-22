import whisper
import os

# Global variable to store the model instance (Lazy Loading)
model = None

def transcribe_audio(filepath, language='en'):
    """
    Transcribes audio using OpenAI's Whisper model.
    Uses the 'base' model for a balance of speed and accuracy.
    """
    global model
    
    if not filepath or not os.path.exists(filepath):
        return "Error: No valid file provided for transcription."

    try:
        # Lazy load the model only when first needed to save startup RAM
        if model is None:
            print("Loading Whisper model (base)... this may take a moment.")
            # 'base' is a good balance. 'tiny' is faster but less accurate. 'small' is better but slower.
            # Using CPU to avoid VRAM issues since we have other models running.
            model = whisper.load_model("base", device="cpu")
            print("Whisper model loaded successfully.")

        print(f"Transcribing {filepath}...")
        
        # Transcribe
        # fp16=False is needed for CPU execution usually
        result = model.transcribe(filepath, fp16=False)
        
        text = result.get('text', '').strip()
        detected_lang = result.get('language', 'unknown')
        
        return f"[Whisper Transcription - Detected Language: {detected_lang}]\n\n{text}"

    except Exception as e:
        print(f"Error during transcription: {e}")
        return f"Error during transcription: {str(e)}"

