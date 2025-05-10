"""
Script to upload videos to S3 for testing with Rekognition.
"""

import os
import sys
import argparse
from typing import List

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.s3_utils import upload_to_s3, upload_files_to_s3

def parse_args():
    parser = argparse.ArgumentParser(description="Upload videos to S3 for Rekognition testing")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--prefix", default="videos", help="S3 key prefix (folder)")
    parser.add_argument("files", nargs="+", help="Video file paths to upload")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Validate files exist
    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return 1
    
    print(f"Uploading {len(args.files)} videos to s3://{args.bucket}/{args.prefix}/")
    
    # Upload files
    s3_uris = upload_files_to_s3(args.files, args.bucket, args.prefix)
    
    print("\nUploaded videos:")
    for uri in s3_uris:
        print(f"  {uri}")
    
    print("\nYou can now use these S3 URIs with the analyze_video_s3() function.")
    return 0

if __name__ == "__main__":
    sys.exit(main())