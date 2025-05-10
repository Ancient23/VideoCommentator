# FastAPI wrapper for vision_llm_service
from fastapi import FastAPI, HTTPException
from summarizer import summarize
from sampler import sample_frames
from collator import build_timeline
from .s3_utils import is_s3_uri
from .vision import analyze_video_s3
import boto3

app = FastAPI()

@app.post("/summarize")
async def summarize_video(path: str):
    """
    Summarize a video from either local path or S3 URL.
    For S3 videos, uses Rekognition Video APIs directly.
    For local videos, samples frames and analyzes individually.
    """
    try:
        # For S3 videos, use Rekognition Video APIs directly
        if is_s3_uri(path):
            events = analyze_video_s3(path)
            timeline = build_timeline(events)
        # For local videos, use frame sampling approach
        else:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
