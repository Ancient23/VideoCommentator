import argparse, json, tempfile, subprocess, boto3, openai
from sampler import sample_frames
from collator import build_timeline
from summarizer import summarize

def main():

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video", type=str, help="Input video file to process")
    group.add_argument("--input-timeline", type=str, help="Use a pregenerated timeline JSON instead of processing a video")
    parser.add_argument("--fps", type=int, default=1)
    parser.add_argument("--chunked", action="store_true", help="Use chunked summarization (for long videos)")
    parser.add_argument("--timeline-json", type=str, help="If set, output the timeline as a JSON file and exit.")
    parser.add_argument("--detect-labels", action="store_true", default=True, help="Enable label detection (default: on)")
    parser.add_argument("--detect-faces", action="store_true", help="Enable face detection")
    parser.add_argument("--detect-celebrities", action="store_true", help="Enable celebrity recognition")
    parser.add_argument("--detect-text", action="store_true", help="Enable text-in-image detection (OCR)")
    parser.add_argument("--style", type=str, default="Sports Commentator", help="Voiceover style (e.g. 'Sports Commentator', 'Morgan Freeman', 'YouTube influencer', etc.)")
    parser.add_argument("--voiceover", action="store_true", help="Generate a voiceover script instead of a summary.")
    parser.add_argument("--voiceover-audio", action="store_true", help="Generate TTS audio for the voiceover script, aligned to video events.")
    args = parser.parse_args()


    if args.input_timeline:
        with open(args.input_timeline, "r", encoding="utf-8") as f:
            timeline = json.load(f)
    else:
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

    from summarizer import summarize_chunked, generate_voiceover_script, generate_voiceover_script_chunked
    from tts import generate_timed_voiceover, tts_openai
    if args.voiceover:
        if args.chunked:
            script = generate_voiceover_script_chunked(timeline, style=args.style)
        else:
            script = generate_voiceover_script(timeline, style=args.style)
        print(f"Voiceover script (style: {args.style}):\n", script)
        if args.voiceover_audio:
            print("Generating timed voiceover audio...")
            audio_segments = generate_timed_voiceover(timeline, script, tts_func=tts_openai)
            for ts, audio_path in audio_segments:
                print(f"Audio segment at {ts:.2f}s: {audio_path}")
    else:
        if args.chunked:
            print("Summary (chunked):\n", summarize_chunked(timeline))
        else:
            print("Summary:\n", summarize(timeline))

if __name__ == "__main__":
    main()
