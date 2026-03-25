import os
import json
import subprocess

print("=== Simple YouTube Upload Using Cookies ===")

# Load metadata
with open("output/metadata.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

video_file = "output/story_video.mp4"

print(f"Uploading video: {meta['title']}")

# yt-dlp upload command
cmd = [
    "yt-dlp",
    "--cookies-from-browser", "chrome",           # Change to "firefox" if you use Firefox
    "--username", "sandeep14394413@gmail.com",    # ← YOUR GMAIL
    "--password", "",                             # Leave empty
    "--title", meta["title"],
    "--description", meta["description"],
    "--tags", ",".join(meta["tags"]),
    "--privacy", "unlisted",                      # Change to "public" later
    video_file
]

try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("✅ Upload command executed successfully!")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("❌ Upload failed")
    print("Error output:")
    print(e.stderr)
    print("\nTips:")
    print("- Make sure you are logged into Chrome with your Gmail")
    print("- Try changing 'chrome' to 'firefox' or 'edge'")
    print("- First test locally: yt-dlp --cookies-from-browser chrome --version")
