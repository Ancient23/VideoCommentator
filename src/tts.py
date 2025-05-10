# Text-to-Speech utilities for voiceover audio generation
# Uses OpenAI TTS API (or fallback to pyttsx3 for local/offline)
import os
import tempfile
from typing import List, Dict, Tuple

try:
    import openai
except ImportError:
    openai = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

def tts_openai(text: str, voice: str = "alloy", output_path: str = None) -> str:
    """
    Generate speech audio from text using OpenAI TTS API.
    Returns the path to the generated audio file.
    """
    if openai is None:
        raise ImportError("openai package is required for OpenAI TTS")
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=voice,
        input=text,
        response_format="mp3",
    ) as response:
        with open(output_path, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
    return output_path

def tts_local(text: str, output_path: str = None) -> str:
    """
    Generate speech audio from text using pyttsx3 (offline, local TTS).
    Returns the path to the generated audio file.
    """
    if pyttsx3 is None:
        raise ImportError("pyttsx3 package is required for local TTS")
    engine = pyttsx3.init()
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    return output_path

def generate_timed_voiceover(events: List[Dict], script: str, tts_func=tts_openai, voice: str = "alloy") -> List[Tuple[float, str]]:
    """
    Given a timeline of events and a voiceover script, split the script into segments aligned to event timestamps.
    Returns a list of (timestamp, audio_path) tuples.
    """
    # Simple alignment: split script into N segments for N events
    if not events or not script:
        return []
    import re
    sentences = re.split(r'(?<=[.!?]) +', script.strip())
    n = min(len(events), len(sentences))
    result = []
    for i in range(n):
        ts = events[i].get("t", i)
        audio_path = tts_func(sentences[i], voice=voice)
        result.append((ts, audio_path))
    return result
