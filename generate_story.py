import os
import json
import asyncio
import subprocess
import random
from edge_tts import Communicate
import google.genai as genai
from google.genai.types import GenerateContentConfig

# ====================== CONFIG ======================
GEMINI_MODEL = "gemini-1.5-flash"
NUM_VIDEOS = 1                      # Start with 1 video for testing
# ===================================================

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MORAL_THEMES = [
    "honesty and friendship", "kindness and sharing", "helping others",
    "never giving up", "being brave", "respecting elders", "teamwork"
]

for video_num in range(NUM_VIDEOS):
    print(f"\n=== Generating High-Quality Cartoon Video {video_num+1} ===")
    
    topic = random.choice(MORAL_THEMES)
    prompt = f"""Write a short, fun moral story for kids (age 4-8) about {topic}. 
    Length: 400-600 words. Simple language, lots of dialogue, vivid descriptions good for cartoon."""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=GenerateContentConfig(temperature=0.8)
    )
    story_text = response.text.strip()

    folder = f"output/cartoon_{video_num+1}"
    os.makedirs(folder, exist_ok=True)

    with open(f"{folder}/story.txt", "w", encoding="utf-8") as f:
        f.write(story_text)

    # Voiceover
    print("Generating voiceover...")
    communicate = Communicate(story_text, "en-US-AvaNeural")
    asyncio.run(communicate.save(f"{folder}/narration.mp3"))

    # Title
    title = f"Cute Cartoon Story: {topic.title()} Adventure | Kids Moral Story"

    # Simple metadata
    metadata = {
        "title": title,
        "description": f"{story_text[:200]}...\n\nHigh Quality AI Cartoon for Kids",
        "tags": ["kids cartoon", "moral story", "cartoon for kids"]
    }
    with open(f"{folder}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    # Create subtitles
    subtitle_file = f"{folder}/subtitles.srt"
    with open(subtitle_file, "w", encoding="utf-8") as f:
        f.write("1\n00:00:01,000 --> 00:05:00,000\n")
        f.write(story_text.replace("\n", "\n\n"))

    print("Creating high-resolution cartoon-style video...")

    escaped_title = title.replace("'", "'\\''")

    # High resolution cartoon video with better styling
    cmd = f"""
ffmpeg -y \
  -f lavfi -i color=c=#1e3a8a:s=1080x1920:d=300 \
  -i {folder}/narration.mp3 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=52:fontcolor=#ffffff:x=(w-text_w)/2:y=80:text='{escaped_title}':shadowcolor=black:shadowx=5:shadowy=5, \
       subtitles={subtitle_file}:force_style='Fontsize=34,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=4,BackColour=&HAA000000,Shadow=3,MarginV=100,Alignment=10'" \
  -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -t 300 -pix_fmt yuv420p \
  {folder}/high_quality_cartoon.mp4
"""

    subprocess.run(cmd, shell=True, check=True)

    print(f"✅ High-Quality Cartoon Video created: {folder}/high_quality_cartoon.mp4")
