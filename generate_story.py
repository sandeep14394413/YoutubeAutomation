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
GEMINI_MODEL = "gemini-1.5-flash"   # Most reliable model right now
NUM_VIDEOS = 2                      # Change this to generate more videos
# ===================================================

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MORAL_THEMES = [
    "honesty and friendship", "kindness and sharing", "helping others",
    "never giving up", "being brave", "respecting elders", "teamwork",
    "forgiveness", "gratitude", "caring for animals"
]

def generate_story():
    topic = random.choice(MORAL_THEMES)
    prompt = f"""Write a complete, fun, engaging moral story for kids (age 4-8) about {topic}.
    Length: 500-700 words. Use simple language, lots of dialogue, vivid descriptions suitable for cartoon animation.
    End with a clear moral lesson."""

    print(f"Generating story about {topic}...")

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=GenerateContentConfig(temperature=0.8)
        )
        story_text = response.text.strip() if response.text else None
    except Exception as e:
        print(f"Error with {GEMINI_MODEL}: {e}")
        story_text = None

    # Fallback if response is empty
    if not story_text:
        print("Using fallback story...")
        story_text = f"Once upon a time, there was a little rabbit named {topic.split()[0].title()}. He learned that {topic} is very important. He helped his friends and everyone was happy. The moral is: {topic} makes the world better."

    return story_text, topic

for video_num in range(NUM_VIDEOS):
    print(f"\n=== Generating High-Quality Cartoon Video {video_num+1}/{NUM_VIDEOS} ===")
    
    story_text, topic = generate_story()

    folder = f"output/cartoon_{video_num+1}"
    os.makedirs(folder, exist_ok=True)

    with open(f"{folder}/story.txt", "w", encoding="utf-8") as f:
        f.write(story_text)

    # Voiceover
    print("Generating voiceover...")
    communicate = Communicate(story_text, "en-US-AvaNeural")
    asyncio.run(communicate.save(f"{folder}/narration.mp3"))

    # Split into scenes
    sentences = re.split(r'(?<=[.!?])\s+', story_text)
    scenes = [ " ".join(sentences[j:j+5]) for j in range(0, len(sentences), 5) ][:8]
    
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

    # Subtitle
    subtitle_file = f"{folder}/subtitles.srt"
    with open(subtitle_file, "w", encoding="utf-8") as f:
        f.write("1\n00:00:01,000 --> 00:05:00,000\n")
        f.write(story_text.replace("\n", "\n\n"))

    # Assemble video
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

print("\n🎉 All cartoon videos generated successfully!")
print("Download them from the Artifacts section.")
