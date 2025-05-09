# vision_llm_service

A local CLI/API-driven service that turns an input video file into a concise textual synopsis using ffmpeg, AWS Rekognition, (optional) Whisper/AWS Transcribe, and OpenAI GPT-4o.

## Features
- Frame sampling with ffmpeg (1 fps by default)
- Image labeling via AWS Rekognition
- (Optional) Audio transcription via Whisper or AWS Transcribe
- Timeline event collation
- LLM-based summarization (OpenAI GPT-4o)
- CLI and optional FastAPI interface

## Quick Start

### Prerequisites
- Python ≥ 3.11
- AWS account with Rekognition (& Transcribe if used) enabled
- OpenAI API key
- ffmpeg installed and in PATH

### Installation
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Configuration
Set environment variables for AWS and OpenAI credentials:
```powershell
$env:AWS_ACCESS_KEY_ID="..."
$env:AWS_SECRET_ACCESS_KEY="..."
$env:AWS_DEFAULT_REGION="us-west-2"
$env:OPENAI_API_KEY="..."
```

### Usage (CLI)
```powershell
python src/main.py --video sample.mp4
```

### Usage (API)
```powershell
uvicorn src.api:app --reload
```

## Project Structure
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
└── README.md
```

See VISION_LLM_SERVICE.md for full architecture and implementation notes.
