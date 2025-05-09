# ffmpeg helpers for frame sampling
import ffmpeg
import os
import tempfile
from typing import List, Tuple

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
