<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Copilot Instructions for vision_llm_service

- This project is a Python CLI/API service that generates concise textual synopses from video files using ffmpeg, AWS Rekognition, optional Whisper/AWS Transcribe, and OpenAI GPT-4o.
- Follow the architecture and workflow described in VISION_LLM_SERVICE.md.
- Use modular, testable code and keep costs and cloud portability in mind.
- All code should be placed under the `src/` directory as per the project layout.
- Use .env for credentials and configuration.
- Provide clear docstrings and comments for all modules.
- Use FastAPI for the optional API interface.
- Use ffmpeg-python for frame extraction, boto3 for AWS, and openai>=1.0 for LLM calls.
- Add retry/backoff and result caching where appropriate.
