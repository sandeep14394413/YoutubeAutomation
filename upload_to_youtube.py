import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

print("=== YouTube Upload Started ===")

creds = Credentials(
    None,
    refresh_token=os.getenv("REFRESH_TOKEN"),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)

print("Trying to refresh token...")

try:
    creds.refresh(Request())
    print("✅ Token refreshed successfully!")
except Exception as e:
    print("❌ TOKEN REFRESH FAILED")
    print("Error:", str(e))
    print("\n" + "="*60)
    print("WHAT TO DO NOW:")
    print("1. Go to: https://developers.google.com/oauthplayground")
    print("2. Click gear icon → Use your own OAuth credentials")
    print("3. Paste your CLIENT_ID and CLIENT_SECRET")
    print("4. Authorize the scope: https://www.googleapis.com/auth/youtube.upload")
    print("5. Copy the NEW Refresh Token")
    print("6. Update the REFRESH_TOKEN secret in GitHub")
    print("="*60)
    raise

print("Building YouTube service...")
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
            "privacyStatus": "unlisted",     # Change to "public" when ready
            "selfDeclaredMadeForKids": True
        }
    },
    media_body=media
)

print("Uploading video to YouTube...")
response = request.execute()

print("✅ SUCCESS! Video uploaded!")
print("Video URL: https://youtu.be/" + response["id"])
