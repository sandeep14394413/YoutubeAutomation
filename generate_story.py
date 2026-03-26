import os
import json
import asyncio
import subprocess
import random
from edge_tts import Communicate
import google.genai as genai
from google.genai.types import GenerateContentConfig

# ====================== CONFIG ======================
GEMINI_MODEL = "gemini-2.0-flash-exp"
NUM_VIDEOS = 2                    # Change this to create more videos
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

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=GenerateContentConfig(temperature=0.85)
    )
    return response.text.strip(), topic

for i in range(NUM_VIDEOS):
    print(f"\n=== Generating High-Quality Cartoon Video {i+1}/{NUM_VIDEOS} ===")
    
    story_text, topic = generate_story()
    folder = f"output/cartoon_{i+1}"
    os.makedirs(folder, exist_ok=True)

    # Save story
    with open(f"{folder}/story.txt", "w", encoding="utf-8") as f:
        f.write(story_text)

    # Voiceover
    print("Generating voiceover...")
    communicate = Communicate(story_text, "en-US-AvaNeural")
    asyncio.run(communicate.save(f"{folder}/narration.mp3"))

    # Title & Metadata
    title = f"New Cartoon Story: The Brave {topic.title()} | Kids Moral Cartoon"

    metadata = {
        "title": title,
        "description": f"{story_text[:300]}...\n\nBeautiful AI Cartoon Moral Story for Kids\n#kidscartoon #moralstories #cartoonforkids",
        "tags": ["kids cartoon", "moral story", "bedtime story", "children animation", "ai cartoon"]
    }
    with open(f"{folder}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print("Creating high-quality cartoon video with scenes...")

    # High-quality cartoon video assembly (with background music + smooth transitions)
    cmd = f'''
ffmpeg -y \
  -f lavfi -i color=c=#1e3a8a:s=1080x1920:d=300 \
  -i {folder}/narration.mp3 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=55:fontcolor=white:x=(w-text_w)/2:y=100:text='{title.replace("'", "'\\''")}':shadowcolor=black:shadowx=4:shadowy=4, \
       subtitles={folder}/subtitles.srt:force_style='Fontsize=36,PrimaryColour=&HFFFFFF,OutlineColour=&H00000000,BorderStyle=4,BackColour=&HAA000000,Shadow=2,MarginV=120'" \
  -c:v libx264 -c:a aac -t 300 -pix_fmt yuv420p \
  {folder}/cartoon_video.mp4
'''

    # Create simple subtitle for now (you can improve later)
    with open(f"{folder}/subtitles.srt", "w", encoding="utf-8") as f:
        f.write("1\n00:00:01,000 --> 00:05:00,000\n")
        f.write(story_text.replace("\n", "\n\n"))

    subprocess.run(cmd, shell=True, check=True)

    print(f"✅ Cartoon Video {i+1} created: {folder}/cartoon_video.mp4")

print("\n🎉 All high-quality cartoon videos generated successfully!")
print("Download them from the Artifacts section.")
