# Audio utilities for muxing/mixing TTS segments with video using ffmpeg-python
import os
import tempfile
from typing import List, Tuple
import ffmpeg

def concat_audio_segments(audio_segments: List[Tuple[float, str]], output_path: str = None) -> str:
    """
    Concatenate audio segments (with optional silence padding) into a single audio file.
    Each segment is a tuple (timestamp, audio_path). Segments are placed at their timestamps.
    Returns the path to the concatenated audio file.
    """
    if not audio_segments:
        raise ValueError("No audio segments provided")
    # Sort by timestamp
    audio_segments = sorted(audio_segments, key=lambda x: x[0])
    # Calculate silence durations between segments
    files = []
    last_end = 0.0
    silence_files = []
    for i, (ts, path) in enumerate(audio_segments):
        if ts > last_end:
            silence_duration = ts - last_end
            silence_path = tempfile.mktemp(suffix="_silence.wav")
            (
                ffmpeg.input('anullsrc=r=22050:cl=mono', f='lavfi', t=silence_duration)
                .output(silence_path, acodec='pcm_s16le', ar=22050, ac=1)
                .overwrite_output()
                .run(quiet=True)
            )
            files.append(silence_path)
            silence_files.append(silence_path)
        files.append(path)
        # Estimate end time (approximate, assumes no overlap)
        try:
            probe = ffmpeg.probe(path)
            duration = float(probe['format']['duration'])
        except Exception:
            duration = 1.0
        last_end = ts + duration
    # Concatenate all files
    concat_list = tempfile.mktemp(suffix="_concat.txt")
    with open(concat_list, 'w') as f:
        for file in files:
            f.write(f"file '{file}'\n")
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
    (
        ffmpeg.input(concat_list, format='concat', safe=0)
        .output(output_path, acodec='pcm_s16le', ar=22050, ac=1)
        .overwrite_output()
        .run(quiet=True)
    )
    # Cleanup silence files
    for s in silence_files:
        try:
            os.remove(s)
        except Exception:
            pass
    os.remove(concat_list)
    return output_path

def mux_audio_to_video(video_path: str, audio_path: str, output_path: str = None) -> str:
    """
    Mux the given audio file into the video, replacing the original audio.
    Returns the path to the muxed video file.
    """
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix="_muxed.mp4")
        os.close(fd)
    (
        ffmpeg.input(video_path)
        .output(audio_path)
        .output(output_path, vcodec='copy', acodec='aac', strict='experimental', shortest=None)
        .overwrite_output()
        .run(quiet=True)
    )
    return output_path
