# AWS Rekognition wrapper
import boto3
from typing import List, Dict

def detect_labels_on_frames(frames: List[str], max_labels=10, min_conf=60) -> List[Dict]:
    rek = boto3.client("rekognition")
    results = []
    for frame_path in frames:
        with open(frame_path, "rb") as img:
            resp = rek.detect_labels(Image={'Bytes': img.read()},
                                     MaxLabels=max_labels, MinConfidence=min_conf)
        results.append(resp["Labels"])
    return results
