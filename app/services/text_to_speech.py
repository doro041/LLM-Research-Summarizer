# app/services/text_to_speech.py
import os
from gtts import gTTS
from app.schemas.summary import PaperSummary

def generate_audio_summary(summary: PaperSummary, output_path: str = "summary_audio.mp3") -> str:
    """Generate audio summary from paper summary using Google Text-to-Speech."""
    
    spoken_text = f"""
    Research Paper Summary.
    
    Title: {summary.title}.
    
    Main Contributions:
    {'. '.join(summary.contributions)}.
    
    Methodology:
    {summary.methodology}.
    
    Results:
    {summary.results}.
    
    Limitations:
    {'. '.join(summary.limitations)}.
    
    End of summary.
    """

    try:
        tts = gTTS(text=spoken_text, lang='en', slow=False)
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Warning: Could not generate audio - {str(e)}")
        print("Install gTTS: pip install gTTS")
        return None


def generate_audio_from_text(text: str, output_path: str = "audio_output.mp3") -> str:
    """Generate audio from any text."""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        return None
