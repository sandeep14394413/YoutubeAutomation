import os
import json
import google.generativeai as genai
from edge_tts import Communicate
import subprocess
import asyncio
from config import STORY_PROMPT, VOICE, VIDEO_DURATION, VIDEO_WIDTH, VIDEO_HEIGHT

# Setup Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# You can change the topic here or make it dynamic later
topic = "honesty and friendship"
prompt = STORY_PROMPT.format(topic=topic)

print("Generating story...")
response = model.generate_content(prompt)
story_text = response.text.strip()

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

# Prepare metadata
title = f"The Honest Little Rabbit | Moral Story for Kids"

metadata = {
    "title": title,
    "description": f"{story_text[:250]}...\n\n🤖 AI Generated Moral Story for Kids\n#kidsstories #moralstories #storytime #bedtimestory",
    "tags": ["kids story", "moral story", "bedtime story", "ai story", "storytime", "children stories"]
}

with open("output/metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

print("Creating video with FFmpeg...")

# Fixed FFmpeg command - no backslash inside f-string expression
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
