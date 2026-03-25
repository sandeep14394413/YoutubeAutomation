import os
import json
import asyncio
import subprocess
from edge_tts import Communicate
import google.genai as genai
from google.genai.types import GenerateContentConfig

# ====================== CONFIG ======================
GEMINI_MODEL = "gemini-2.5-flash"

STORY_PROMPT = """Write a complete, engaging moral story for kids (age 4-8) 
about {topic}. The story should be 550-750 words, have a clear beginning, 
middle and end, and teach a good moral lesson. Make it fun and easy to understand."""

VOICE = "en-US-AvaNeural"   # Warm female voice

VIDEO_DURATION = 300
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
# ===================================================

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

topic = "honesty and friendship"
prompt = STORY_PROMPT.format(topic=topic)

print("Generating story...")
response = client.models.generate_content(
    model=GEMINI_MODEL,
    contents=prompt,
    config=GenerateContentConfig(temperature=0.7)
)

story_text = response.text.strip() if response.text else "No story generated."
print(f"Story generated! Length: {len(story_text)} characters")

os.makedirs("output", exist_ok=True)

with open("output/story_text.txt", "w", encoding="utf-8") as f:
    f.write(story_text)

# Voiceover
print("Generating narration...")
communicate = Communicate(story_text, VOICE)
audio_file = "output/narration.mp3"
asyncio.run(communicate.save(audio_file))
print("Voiceover generated!")

# Title & Metadata
title = "The Honest Little Rabbit | Moral Story for Kids"

metadata = {
    "title": title,
    "description": f"{story_text[:250]}...\n\n🤖 AI Generated Moral Story for Kids\n#kidsstories #moralstories #storytime #bedtimestory",
    "tags": ["kids story", "moral story", "bedtime story", "ai story", "storytime"]
}

with open("output/metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

# Subtitle file
subtitle_file = "output/subtitles.srt"
with open(subtitle_file, "w", encoding="utf-8") as f:
    f.write("1\n00:00:01,000 --> 00:05:00,000\n")
    f.write(story_text.replace("\n", "\n\n"))

print("Creating beautiful video with background + music + animated subtitles...")

escaped_title = title.replace("'", "'\\''")

cmd = f'''
ffmpeg -y \
-i https://assets.mixkit.co/videos/preview/12345/12345-small.mp4 \   # Soft nature background (replace if needed)
-i {audio_file} \
-i https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3 \   # Calm background music (replace with better free link)
-filter_complex "[0:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},loop=loop=-1:size=1:start=0[v]; \
 [v]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=60:fontcolor=white:x=(w-text_w)/2:y=120:text='{escaped_title}':shadowcolor=black:shadowx=3:shadowy=3[title]; \
 [title]subtitles={subtitle_file}:force_style='Fontsize=38,PrimaryColour=&HFFFFFF,OutlineColour=&H00000000,BorderStyle=4,BackColour=&H80000000,Shadow=2,MarginV=100,Alignment=10'[outv]" \
-map "[outv]" -map 1:a -map 2:a \
-filter_complex "[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=2[aout]" \
-c:v libx264 -c:a aac -t {VIDEO_DURATION} -pix_fmt yuv420p \
output/story_video.mp4
'''

subprocess.run(cmd, shell=True, check=True)

print("✅ Beautiful video created: output/story_video.mp4")
print("It now has background, calm music, and nice animated subtitles!")
