import os
import json
import subprocess

print("=== YouTube Upload Started (using yt-dlp) ===")

# Load metadata
with open("output/metadata.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

video_file = "output/story_video.mp4"

print(f"Video title: {meta['title']}")

# Correct yt-dlp upload command
cmd = [
    "yt-dlp",
    "--cookies-from-browser", "chrome",                    # Change to "firefox" if needed
    "--username", "sandeep14394413@gmail.com",             # Your Gmail
    "--password", "",
    "--title", meta["title"],
    "--description", meta["description"],
    "--tags", ",".join(meta["tags"]),
    "--privacy-status", "unlisted",                        # or "public"
    "--no-mtime",
    video_file
]

print("Running upload command...")

try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("✅ Upload command completed!")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("❌ Upload failed")
    print("Error:")
    print(e.stderr)
    print("\nSuggestion:")
    print("Try changing '--cookies-from-browser chrome' to '--cookies-from-browser firefox' or '--cookies-from-browser edge'")
