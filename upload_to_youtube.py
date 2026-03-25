import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

print("Uploading to YouTube...")

creds = Credentials(
    None,
    refresh_token=os.getenv("REFRESH_TOKEN"),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)

# Force refresh
creds.refresh(Request())

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
            "privacyStatus": "unlisted",      # Change to "public" after testing
            "selfDeclaredMadeForKids": True
        }
    },
    media_body=media
)

response = request.execute()
print("✅ Upload successful!")
print("Video URL: https://youtu.be/" + response["id"])
