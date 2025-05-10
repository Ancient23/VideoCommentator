# AWS Rekognition wrapper
import time
import boto3
from typing import List, Dict
from .s3_utils import is_s3_uri, parse_s3_uri

def detect_labels_on_frames(frames: List[str], max_labels=10, min_conf=60) -> List[Dict]:
    """Detect labels on a list of local image frame files."""
    rek = boto3.client("rekognition")
    results = []
    for frame_path in frames:
        with open(frame_path, "rb") as img:
            resp = rek.detect_labels(Image={'Bytes': img.read()},
                                     MaxLabels=max_labels, MinConfidence=min_conf)
        results.append(resp["Labels"])
    return results

def wait_for_job(job_id: str, rekognition_client) -> str:
    """Wait for a Rekognition video job to complete. Returns final status."""
    while True:
        response = rekognition_client.get_label_detection(JobId=job_id)
        status = response['JobStatus']
        if status in ['SUCCEEDED', 'FAILED']:
            return status
        time.sleep(5)  # Poll every 5 seconds

def analyze_video_s3(video_uri: str, min_confidence: float = 60.0) -> List[Dict]:
    """
    Analyze a video stored in S3 using Rekognition Video APIs.
    Returns a list of label detection events with timestamps.
    """
    bucket, key = parse_s3_uri(video_uri)
    rek = boto3.client('rekognition')
    
    # Start async video analysis
    response = rek.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        MinConfidence=min_confidence,
    )
    
    job_id = response['JobId']
    final_status = wait_for_job(job_id, rek)
    
    if final_status == 'FAILED':
        raise Exception(f"Video analysis failed for {video_uri}")
    
    # Get results, handling pagination
    events = []
    next_token = None
    
    while True:
        if next_token:
            response = rek.get_label_detection(JobId=job_id, NextToken=next_token)
        else:
            response = rek.get_label_detection(JobId=job_id)
        
        for label in response['Labels']:
            timestamp = float(label['Timestamp']) / 1000.0  # Convert to seconds
            events.append({
                "t": timestamp,
                "labels": [{
                    "Name": label['Label']['Name'],
                    "Confidence": label['Label']['Confidence'],
                    "Parents": [{"Name": parent['Name']} for parent in label['Label'].get('Parents', [])]
                }]
            })
        
        if 'NextToken' in response:
            next_token = response['NextToken']
        else:
            break
            
    return sorted(events, key=lambda x: x['t'])
