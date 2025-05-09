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
    parser.add_argument("--detect-labels", action="store_true", default=True, help="Enable label detection (default: on)")
    parser.add_argument("--detect-faces", action="store_true", help="Enable face detection")
    parser.add_argument("--detect-celebrities", action="store_true", help="Enable celebrity recognition")
    parser.add_argument("--detect-text", action="store_true", help="Enable text-in-image detection (OCR)")
    args = parser.parse_args()


    frames = sample_frames(args.video, fps=args.fps)        # ffmpeg
    rek = boto3.client("rekognition")
    events = []
    for ts, frame_path in frames:
        event = {"t": ts}
        with open(frame_path, "rb") as img:
            img_bytes = img.read()
            if args.detect_labels:
                resp = rek.detect_labels(Image={'Bytes': img_bytes}, MaxLabels=10, MinConfidence=60)
                event["labels"] = resp.get("Labels", [])
            if args.detect_faces:
                resp = rek.detect_faces(Image={'Bytes': img_bytes}, Attributes=["ALL"])
                event["faces"] = resp.get("FaceDetails", [])
            if args.detect_celebrities:
                resp = rek.recognize_celebrities(Image={'Bytes': img_bytes})
                event["celebrities"] = resp.get("CelebrityFaces", [])
            if args.detect_text:
                resp = rek.detect_text(Image={'Bytes': img_bytes})
                event["text_detections"] = resp.get("TextDetections", [])
        events.append(event)

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
