import os
import json
import subprocess

print("=== Simple YouTube Upload Using Cookies ===")

# Load metadata
with open("output/metadata.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

video_file = "output/story_video.mp4"

print(f"Uploading: {meta['title']}")

# Command using yt-dlp with cookies
cmd = [
    "yt-dlp",
    "--cookies-from-browser", "chrome",   # Change to "firefox" or "edge" if you use different browser
    "--username", "sandeep14394413@gmail.com",   # ← CHANGE TO YOUR GMAIL
    "--password", "",                        # Leave empty - it will prompt or use cookies
    "--title", meta["title"],
    "--description", meta["description"],
    "--tags", ",".join(meta["tags"]),
    "--privacy", "unlisted",                 # Change to "public" when ready
    "--no-mtime",
    video_file
]

try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("✅ Upload command executed!")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("❌ Upload failed")
    print(e.stderr)
    print("\nCommon fixes:")
    print("1. Make sure you are logged into Chrome with your YouTube Gmail")
    print("2. Try changing '--cookies-from-browser chrome' to 'firefox' or 'edge'")
    print("3. Run 'yt-dlp --cookies-from-browser chrome' locally first to test")
