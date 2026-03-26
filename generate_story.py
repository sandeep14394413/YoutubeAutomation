import os
import json
import asyncio
import subprocess
import random
from edge_tts import Communicate

print("=== Starting High-Quality Kids Cartoon Generator ===")

# Hard-coded fallback story (in case API fails)
story_text = """Once upon a time in a sunny green forest, there lived a little rabbit named Hopper. Hopper had many friends, but he was not very honest. One day, his best friend Squirrel lost his favorite shiny acorn. Hopper had found it but he hid it because he wanted to keep it for himself.

Later, Squirrel was very sad. Hopper saw his friend crying and felt bad. He remembered that true friendship is more important than any shiny thing. Hopper went to Squirrel and gave back the acorn. He said, "I'm sorry I was not honest. I learned that honesty makes friendships stronger."

Squirrel smiled and hugged Hopper. From that day, they became the best of friends forever. 

The moral of the story is: Honesty is the best policy and it makes true friendship stronger."""

print("Using story (fallback mode for stability)...")
print("Story length:", len(story_text))

folder = "output/cartoon_1"
os.makedirs(folder, exist_ok=True)

with open(f"{folder}/story.txt", "w", encoding="utf-8") as f:
    f.write(story_text)

# Voiceover
print("Generating voiceover...")
communicate = Communicate(story_text, "en-US-AvaNeural")
asyncio.run(communicate.save(f"{folder}/narration.mp3"))
print("Voiceover generated!")

# Title
title = "The Honest Little Rabbit | Cute Moral Cartoon for Kids"

metadata = {
    "title": title,
    "description": "Beautiful AI generated moral story cartoon for kids.\n#kidscartoon #moralstories",
    "tags": ["kids cartoon", "moral story", "cartoon for kids"]
}

with open(f"{folder}/metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

# Subtitle
subtitle_file = f"{folder}/subtitles.srt"
with open(subtitle_file, "w", encoding="utf-8") as f:
    f.write("1\n00:00:01,000 --> 00:05:00,000\n")
    f.write(story_text.replace("\n", "\n\n"))

print("Creating high-resolution cartoon video...")

escaped_title = title.replace("'", "'\\''")

cmd = f"""
ffmpeg -y \
  -f lavfi -i color=c=#1e3a8a:s=1080x1920:d=300 \
  -i {folder}/narration.mp3 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=52:fontcolor=white:x=(w-text_w)/2:y=80:text='{escaped_title}':shadowcolor=black:shadowx=5:shadowy=5, \
       subtitles={subtitle_file}:force_style='Fontsize=34,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=4,BackColour=&HAA000000,Shadow=3,MarginV=100,Alignment=10'" \
  -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -t 300 -pix_fmt yuv420p \
  {folder}/high_quality_cartoon.mp4
"""

subprocess.run(cmd, shell=True, check=True)

print("✅ High-Quality Cartoon Video created successfully!")
print(f"File location: {folder}/high_quality_cartoon.mp4")
print("You can now download it from the Artifacts section.")
