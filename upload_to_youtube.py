import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

print("=== Starting YouTube Upload Debug ===")

creds = Credentials(
    None,
    refresh_token=os.getenv("REFRESH_TOKEN"),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)

print("Attempting to refresh token...")

try:
    creds.refresh(Request())
    print("✅ Token refreshed successfully!")
except Exception as e:
    print("❌ Refresh failed!")
    print("Error type:", type(e).__name__)
    print("Full error message:", str(e))
    raise

youtube = build("youtube", "v3", credentials=creds)

with open("output/metadata.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

media = MediaFileUpload("output/story_video.mp4", chunksize=-1, resumable=True)

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta["tags"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": True
        }
    },
    media_body=media
)

print("Uploading video...")
response = request.execute()
print("✅ SUCCESS! Video uploaded!")
print("Video URL: https://youtu.be/" + response["id"])
