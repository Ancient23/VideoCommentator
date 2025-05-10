# Uploading Videos to S3 for Rekognition Testing

This guide explains how to upload videos to your S3 bucket for testing with AWS Rekognition.

## Prerequisites

1. **AWS CLI installed and configured**
   - Install AWS CLI: https://aws.amazon.com/cli/
   - Configure with your credentials: `aws configure`
   - Make sure you have permissions to upload to S3 and use Rekognition

2. **S3 Bucket Created**
   - Create an S3 bucket in your AWS account if you don't have one already
   - Note: Bucket names must be globally unique

## Method 1: Using the Upload Script

We've created a helper script to make uploading videos easy:

```bash
# Navigate to your project directory
cd c:\Github\VideoCommentator

# Run the upload script
python src/upload_videos.py --bucket YOUR_BUCKET_NAME --prefix videos path/to/video1.mp4 path/to/video2.mp4
```

This will upload your videos and print the S3 URIs you can use with the `analyze_video_s3()` function.

## Method 2: Using AWS CLI

You can also use the AWS CLI directly:

```bash
# Upload a single video
aws s3 cp path/to/video.mp4 s3://YOUR_BUCKET_NAME/videos/

# Upload multiple videos
aws s3 cp path/to/videos/ s3://YOUR_BUCKET_NAME/videos/ --recursive
```

## Method 3: Using AWS Console

1. Log in to the AWS Management Console
2. Navigate to S3
3. Select your bucket
4. Click "Upload" and follow the prompts to upload your videos

## Using the Videos with Rekognition

After uploading, you can use the S3 URIs with your code:

```python
from src.vision import analyze_video_s3

# Example S3 URI format
video_uri = "s3://YOUR_BUCKET_NAME/videos/your_video.mp4"

# Analyze the video
results = analyze_video_s3(video_uri)
```

## Troubleshooting

- **Access Denied**: Check your AWS credentials and bucket permissions
- **Region Issues**: Make sure your S3 bucket and Rekognition are in the same region
- **File Size**: Large videos may take longer to upload and process