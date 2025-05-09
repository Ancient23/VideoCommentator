# FastAPI wrapper for vision_llm_service
from fastapi import FastAPI
from summarizer import summarize
from sampler import sample_frames
from collator import build_timeline
import boto3

app = FastAPI()

@app.post("/summarize")
async def summarize_video(path: str):
    frames = sample_frames(path)
    rek = boto3.client("rekognition")
    events = []
    for ts, frame_path in frames:
        with open(frame_path, "rb") as img:
            resp = rek.detect_labels(Image={'Bytes': img.read()},
                                     MaxLabels=10, MinConfidence=60)
        events.append({"t": ts, "labels": resp["Labels"]})
    timeline = build_timeline(events)
    summary = summarize(timeline)
    return {"summary": summary}
