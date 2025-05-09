# Timeline builder: merges label detections and transcript
from typing import List, Dict

def build_timeline(events: List[Dict], transcript: List[Dict] = None) -> List[Dict]:
    timeline = events.copy()
    if transcript:
        timeline.extend(transcript)
    timeline.sort(key=lambda x: x.get("t", 0))
    return timeline
