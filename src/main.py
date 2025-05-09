import argparse, json, tempfile, subprocess, boto3, openai
from sampler import sample_frames
from collator import build_timeline
from summarizer import summarize

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--fps", type=int, default=1)
    parser.add_argument("--chunked", action="store_true", help="Use chunked summarization (for long videos)")
    parser.add_argument("--timeline-json", type=str, help="If set, output the timeline as a JSON file and exit.")
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

    if args.timeline_json:
        with open(args.timeline_json, "w", encoding="utf-8") as f:
            json.dump(timeline, f, ensure_ascii=False, indent=2)
        print(f"Timeline written to {args.timeline_json}")
        return

    if args.chunked:
        from summarizer import summarize_chunked
        print("Summary (chunked):\n", summarize_chunked(timeline))
    else:
        print("Summary:\n", summarize(timeline))

if __name__ == "__main__":
    main()
