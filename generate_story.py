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
GEMINI_MODEL = "gemini-2.0-flash-exp"
NUM_VIDEOS = 2                    # Number of random cartoons to generate per run
SCENES_PER_VIDEO = 8              # Number of cartoon scenes per video
# ===================================================

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MORAL_THEMES = [
    "honesty and friendship", "kindness and sharing", "helping others",
    "never giving up", "being brave", "respecting elders", "teamwork",
    "forgiveness", "gratitude", "caring for animals"
]

def split_into_scenes(story_text):
    # Simple scene splitting (you can improve later with better prompting)
    sentences = re.split(r'(?<=[.!?])\s+', story_text)
    scenes = []
    chunk_size = max(1, len(sentences) // SCENES_PER_VIDEO)
    for j in range(0, len(sentences), chunk_size):
        scene = " ".join(sentences[j:j+chunk_size])
        if scene.strip():
            scenes.append(scene)
    return scenes[:SCENES_PER_VIDEO]

for video_num in range(NUM_VIDEOS):
    print(f"\n=== Generating High-Quality Cartoon Video {video_num+1}/{NUM_VIDEOS} ===")
    
    topic = random.choice(MORAL_THEMES)
    prompt = f"""Write a complete, fun, engaging moral story for kids (age 4-8) about {topic}.
    Length: 500-700 words. Use simple language, lots of dialogue, vivid descriptions suitable for cartoon animation.
    End with a clear moral lesson."""

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

    # Generate voiceover
    print("Generating voiceover...")
    communicate = Communicate(story_text, "en-US-AvaNeural")
    asyncio.run(communicate.save(f"{folder}/narration.mp3"))

    # Split into scenes and generate cartoon images (using placeholder style prompt for now)
    scenes = split_into_scenes(story_text)
    print(f"Creating {len(scenes)} cartoon scenes...")

    for idx, scene in enumerate(scenes):
        scene_prompt = f"Cute colorful Pixar-style cartoon illustration for kids story: {scene}. Bright colors, friendly characters, simple background, vertical 9:16 aspect ratio, high quality, vibrant, happy mood"
        # Note: In real production, you would call an image generation API here (e.g., Gemini Image, Ideogram, Flux, etc.)
        # For now, we use a placeholder solid background with text overlay. We can add real image gen later.

    # Title
    title = f"New Cartoon Story: The Brave {topic.title()} | Kids Moral Cartoon"

    metadata = {
        "title": title,
        "description": f"{story_text[:300]}...\n\nBeautiful AI Cartoon Moral Story for Kids\n#kidscartoon #moralstories #cartoonforkids",
        "tags": ["kids cartoon", "moral story", "bedtime story", "children animation", "ai cartoon"]
    }
    with open(f"{folder}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    # Create subtitles
    subtitle_file = f"{folder}/subtitles.srt"
    with open(subtitle_file, "w", encoding="utf-8") as f:
        f.write("1\n00:00:01,000 --> 00:05:00,000\n")
        f.write(story_text.replace("\n", "\n\n"))

    # Final video assembly (dark elegant background + subtitles + music simulation)
    print("Assembling final cartoon video...")
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

    print(f"✅ High-Quality Cartoon Video {video_num+1} ready: {folder}/cartoon_video.mp4")

print("\n🎉 All cartoon videos generated!")
print("Download them from the Artifacts section in GitHub Actions.")
