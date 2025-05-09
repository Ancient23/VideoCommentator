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
