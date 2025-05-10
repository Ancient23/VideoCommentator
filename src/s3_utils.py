"""S3 utilities for downloading/uploading files."""

import os
import tempfile
import boto3
from urllib.parse import urlparse
from typing import Optional, List

def is_s3_uri(uri: str) -> bool:
    """Returns True if uri is an S3 URI (s3://bucket/key)."""
    if not uri:
        return False
    try:
        parsed = urlparse(uri)
        return parsed.scheme == 's3'
    except:
        return False

def parse_s3_uri(uri: str) -> tuple[str, str]:
    """Parse an S3 URI into (bucket, key) tuple."""
    parsed = urlparse(uri)
    if parsed.scheme != 's3':
        raise ValueError(f"Not an S3 URI: {uri}")
    return parsed.netloc, parsed.path.lstrip('/')

def download_from_s3(uri: str, target_path: str = None) -> str:
    """
    Download a file from S3 to a local path.
    If target_path is None, downloads to a temporary file.
    Returns the local file path.
    """
    bucket, key = parse_s3_uri(uri)
    
    if target_path is None:
        # Create temp file with same extension as source
        _, ext = os.path.splitext(key)
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        target_path = temp.name
        temp.close()

    s3 = boto3.client('s3')
    s3.download_file(bucket, key, target_path)
    return target_path
def upload_to_s3(local_file_path: str, bucket: str, key: str = None) -> str:
    """
    Upload a local file to an S3 bucket.
    If key is not provided, uses the filename from local_file_path.
    Returns the S3 URI of the uploaded file.
    """
    if key is None:
        key = os.path.basename(local_file_path)
    
    s3 = boto3.client('s3')
    s3.upload_file(local_file_path, bucket, key)
    return f"s3://{bucket}/{key}"

def upload_files_to_s3(local_file_paths: List[str], bucket: str, prefix: str = "") -> List[str]:
    """
    Upload multiple local files to an S3 bucket.
    Returns a list of S3 URIs for the uploaded files.
    """
    s3_uris = []
    for file_path in local_file_paths:
        filename = os.path.basename(file_path)
        key = f"{prefix.rstrip('/')}/{filename}" if prefix else filename
        s3_uri = upload_to_s3(file_path, bucket, key)
        s3_uris.append(s3_uri)
    return s3_uris