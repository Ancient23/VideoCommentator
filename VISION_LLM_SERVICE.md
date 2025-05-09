# VISION_LLM_SERVICE.md

## 1  Objective

Build a local CLI-/API-driven service that turns an input video file into a concise textual synopsis.  
It should be easy to understand, cost-predictable, and cloud-portable.

---

## 2  System Architecture

```
┌──────────────┐   ffmpeg    ┌──────────────┐  boto3   ┌──────────────┐   HTTP
│  Video File  │ ─────────► │ Frame Sampler │ ───────► │ Rekognition  │◄───AWS
└──────────────┘             └──────────────┘          └──────────────┘
                                   │ labels JSON                  │ transcript JSON
                                   ▼                              ▼
                           ┌──────────────────┐          ┌──────────────────┐
                           │ (opt) Whisper /  │          │  Event Collator  │
                           │  AWS Transcribe  │──────────►──────────────────│
                           └──────────────────┘                         │
                                   │ timeline                           │
                                   ▼                                    │
                            ┌────────────────────┐   openai‑python      │
                            │    LLM Summarizer  │──────────────────────┘
                            └────────────────────┘
```

---

## 3  Key Components

### 3.1 Frame Sampler
* **ffmpeg** command extracts ~1 fps JPEGs (`ffmpeg -i input.mp4 -vf fps=1 frames/%04d.jpg`). 
* Keeps the Rekognition bill tiny—only the sampled frames are sent.

### 3.2 AWS Rekognition Client
* Use `boto3.client("rekognition").detect_labels()` for each frame (images)  
  * For long videos switch to the asynchronous `StartLabelDetection` flow later.  
* Typical JSON fields: `Name`, `Confidence`, `Parents`.  
* **Cost note:** first 1 000 images per month are free; after that you pay per image.  

### 3.3 (Optional) Audio Transcription
* **Offline**: run `whisper-timestamped` locally.  
* **Cloud**: `boto3.client("transcribe").start_transcription_job`.  

### 3.4 Event Collator
* Merge label detections (by timecode) with any transcript segments into a compact timeline list.

### 3.5 LLM Summarizer
* Call OpenAI GPT-4o with a few-shot prompt:  
  > “Given this JSON timeline, write ≤4 sentences describing the main events and setting.”  
* The official Python SDK is `openai>=1.0`.  

---

## 4  Project Layout

```
vision_llm_service/
├── src/
│   ├── main.py            # CLI entry point
│   ├── api.py             # FastAPI wrapper (optional)
│   ├── sampler.py         # ffmpeg helpers
│   ├── vision.py          # Rekognition wrapper
│   ├── transcribe.py      # Whisper / Transcribe wrapper
│   ├── collator.py        # timeline builder
│   └── summarizer.py      # OpenAI call
├── requirements.txt
└── README.md              # ← this file or symlink
```

---

## 5  Quick Start

### 5.1 Prerequisites
* Python ≥ 3.11  
* AWS account with Rekognition (& Transcribe if used) enabled  
* OpenAI API key (or Bedrock equivalent)  
* Docker (optional for clean env)  

### 5.2 Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` minimal set:

```text
boto3>=1.34
ffmpeg-python>=0.2
openai>=1.0
python-dotenv>=1.0
fastapi[all]>=0.111   # only if you expose an HTTP API
```

### 5.3 Configure Credentials

```powershell
$env:AWS_ACCESS_KEY_ID="..."
$env:AWS_SECRET_ACCESS_KEY="..."
$env:AWS_DEFAULT_REGION="us-west-2"
$env:OPENAI_API_KEY="..."
```

Environment variables are the simplest way for quick tests.  

### 5.4 Run a One-Shot Summary

```powershell
python src/main.py --video sample.mp4
# → outputs summary paragraph + optionally summary.json
```

### 5.5 Run as a Local API (FastAPI)

```powershell
uvicorn src.api:app --reload
# POST /summarize {"path":"sample.mp4"}
```

FastAPI auto-generates Swagger docs for quick pokes.  

---

## 6  main.py (abbreviated)

```python
import argparse, json, tempfile, subprocess, boto3, openai
from sampler import sample_frames
from collator import build_timeline
from summarizer import summarize

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--fps", type=int, default=1)
    args = parser.parse_args()

    frames = sample_frames(args.video, fps=args.fps)        # ffmpeg
    rek = boto3.client("rekognition")
    events = []
    for ts, frame_path in frames:
        with open(frame_path, "rb") as img:
            resp = rek.detect_labels(Image={'Bytes': img.read()},
                                     MaxLabels=10, MinConfidence=60)
        events.append({"t": ts, "labels": resp["Labels"]})

    timeline = build_timeline(events)                       # + transcript if any
    print("Summary:\n", summarize(timeline))               # GPT‑4o

if __name__ == "__main__":
    main()
```

*(Full implementations live in their respective modules.)*

---

## 7  Next Steps

1. Swap synchronous image calls for `StartLabelDetection` on S3-hosted videos to test longer footage.  
2. Add retry/backoff and result caching for cheaper iterative runs.  
3. Containerize with a slim Python base image; publish to ECR.  
4. Wire an **EventBridge → Lambda → Step Functions** pipeline for batch processing later.  
5. Explore Rekognition **Custom Labels** if generic labels aren’t descriptive enough.
