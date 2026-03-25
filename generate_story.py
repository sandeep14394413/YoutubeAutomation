import os
import json
import asyncio
import subprocess
from edge_tts import Communicate

# New official Google GenAI SDK (recommended in 2026)
import google.genai as genai
from google.genai.types import GenerateContentConfig

# ====================== CONFIG ======================
GEMINI_MODEL = "gemini-2.5-flash"          # Best free/fast model in March 2026

STORY_PROMPT = """Write a complete, engaging moral story for kids (age 4-8) 
about {topic}. The story should be 550-750 words, have a clear beginning, 
middle and end, and teach a good moral lesson. Make it fun and easy to understand."""

VOICE = "en-US-AvaNeural"                  # Warm female voice

VIDEO_DURATION = 300                       # 5 minutes
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920                        # Vertical 9:16
# ===================================================

# Setup Gemini (new SDK)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

topic = "honesty and friendship"           # Change this anytime
prompt = STORY_PROMPT.format(topic=topic)

print("Generating story with Gemini 2.5 Flash...")
response = client.models.generate_content(
    model=GEMINI_MODEL,
    contents=prompt,
    config=GenerateContentConfig(temperature=0.7)
)

story_text = response.text.strip() if response.text else "Error: No story generated."

print(f"Story generated! Length: {len(story_text)} characters")

# Create output folder
os.makedirs("output", exist_ok=True)

# Save raw story
with open("output/story_text.txt", "w", encoding="utf-8") as f:
    f.write(story_text)

# Generate voiceover
print("Generating narration...")
communicate = Communicate(story_text, VOICE)
audio_file = "output/narration.mp3"
asyncio.run(communicate.save(audio_file))
print("Voiceover generated!")

# Prepare metadata for YouTube
title = f"The Honest Little Rabbit | Moral Story for Kids"

metadata = {
    "title": title,
    "description": f"{story_text[:250]}...\n\n🤖 AI Generated Moral Story for Kids\n#kidsstories #moralstories #storytime #bedtimestory",
    "tags": ["kids story", "moral story", "bedtime story", "ai story", "storytime", "children stories"]
}

with open("output/metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

print("Creating video with FFmpeg...")

# Safe escaping for FFmpeg
escaped_title = title.replace("'", "'\\''")
escaped_text = story_text.replace("'", "'\\''")[:700]

cmd = f'''
ffmpeg -y -f lavfi -i color=c=black:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:d={VIDEO_DURATION} \
-i {audio_file} \
-vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=180:text='{escaped_title}', \
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:fontsize=32:fontcolor=white:x=(w-text_w)/2:y=h/2:text='{escaped_text}'" \
-c:v libx264 -c:a aac -t {VIDEO_DURATION} -pix_fmt yuv420p output/story_video.mp4
'''

subprocess.run(cmd, shell=True, check=True)

print("✅ Video created successfully: output/story_video.mp4")
