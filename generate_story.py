import os
import json
import asyncio
import subprocess
import random
import re
from edge_tts import Communicate
import google.genai as genai
from google.genai.types import GenerateContentConfig

# ====================== CONFIG ======================
# Most stable model as of March 2026
GEMINI_MODEL = "gemini-1.5-pro"   

NUM_VIDEOS = 2                    # How many random cartoon videos to generate per run
# ===================================================

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MORAL_THEMES = [
    "honesty and friendship", "kindness and sharing", "helping others",
    "never giving up", "being brave", "respecting elders", "teamwork",
    "forgiveness", "gratitude", "caring for animals"
]

def split_into_scenes(story_text, num_scenes=8):
    sentences = re.split(r'(?<=[.!?])\s+', story_text)
    chunk_size = max(1, len(sentences) // num_scenes)
    scenes = []
    for j in range(0, len(sentences), chunk_size):
        scene = " ".join(sentences[j:j + chunk_size])
        if scene.strip():
            scenes.append(scene.strip())
    return scenes[:num_scenes]

for video_num in range(NUM_VIDEOS):
    print(f"\n=== Generating High-Quality Cartoon Video {video_num+1}/{NUM_VIDEOS} ===")
    
    topic = random.choice(MORAL_THEMES)
    prompt = f"""Write a complete, fun, engaging moral story for kids (age 4-8) about {topic}.
    Length: 500-700 words. Use simple language, lots of dialogue, vivid descriptions suitable for cartoon animation.
    End with a clear moral lesson."""

    print("Generating story...")
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=GenerateContentConfig(temperature=0.85)
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

    # Split story into scenes for future cartoon images
    scenes = split_into_scenes(story_text)
    print(f"Split into {len(scenes)} scenes for cartoon images")

    # Save scenes for future image generation
    with open(f"{folder}/scenes.json", "w", encoding="utf-8") as f:
        json.dump(scenes, f, indent=2)

    # Title & Metadata
    title = f"New Cartoon Story: The Brave {topic.title()} | Kids Moral Cartoon"

    metadata = {
        "title": title,
        "description": f"{story_text[:300]}...\n\nBeautiful AI Cartoon Moral Story for Kids\n#kidscartoon #moralstories #cartoonforkids",
        "tags": ["kids cartoon", "moral story", "bedtime story", "children animation", "ai cartoon"]
    }
    with open(f"{folder}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    # Subtitle file
    subtitle_file = f"{folder}/subtitles.srt"
    with open(subtitle_file, "w", encoding="utf-8") as f:
        f.write("1\n00:00:01,000 --> 00:05:00,000\n")
        f.write(story_text.replace("\n", "\n\n"))

    # Assemble video (dark elegant background + clear subtitles)
    print("Assembling cartoon video...")
    escaped_title = title.replace("'", "'\\''")

    cmd = f"""
ffmpeg -y \
  -f lavfi -i color=c=#0f3460:s=1080x1920:d=300 \
  -i {folder}/narration.mp3 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=55:fontcolor=white:x=(w-text_w)/2:y=100:text='{escaped_title}':shadowcolor=black:shadowx=4:shadowy=4, \
       subtitles={subtitle_file}:force_style='Fontsize=36,PrimaryColour=&HFFFFFF,OutlineColour=&H00000000,BorderStyle=4,BackColour=&HAA000000,Shadow=2,MarginV=120,Alignment=10'" \
  -c:v libx264 -c:a aac -t 300 -pix_fmt yuv420p \
  {folder}/cartoon_video.mp4
"""

    subprocess.run(cmd, shell=True, check=True)

    print(f"✅ Cartoon Video {video_num+1} created: {folder}/cartoon_video.mp4")

print("\n🎉 All high-quality cartoon videos generated successfully!")
print("Download them from the Artifacts section.")
