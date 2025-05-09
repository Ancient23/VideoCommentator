# ffmpeg helpers for frame sampling

# Ensure the bundled ffmpeg binary is used (Windows, project-local)
import os
import sys
import tempfile
from typing import List, Tuple
import ffmpeg

# Prepend the bundled ffmpeg bin directory to PATH if not already present
FFMPEG_BIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools', 'ffmpeg-7.1.1-essentials_build', 'bin'))
if FFMPEG_BIN_DIR not in os.environ["PATH"]:
    os.environ["PATH"] = FFMPEG_BIN_DIR + os.pathsep + os.environ["PATH"]

def sample_frames(video_path: str, fps: int = 1) -> List[Tuple[float, str]]:
    """Extract frames from video at given fps. Returns list of (timestamp, frame_path)."""
    out_dir = tempfile.mkdtemp(prefix="frames_")
    frame_pattern = os.path.join(out_dir, "%04d.jpg")
    (
        ffmpeg
        .input(video_path)
        .output(frame_pattern, vf=f"fps={fps}", start_number=0)
        .run(quiet=True, overwrite_output=True)
    )
    frames = sorted(os.listdir(out_dir))
    return [(i / fps, os.path.join(out_dir, f)) for i, f in enumerate(frames)]
