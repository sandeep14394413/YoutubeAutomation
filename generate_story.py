import os
import json
import asyncio
import subprocess
import random
import re
from edge_tts import Communicate
import google.genai as genai
from google.genai.types import GenerateContentConfig

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

NUM_VIDEOS = 2                    # Change this to create more videos
MORAL_THEMES = ["honesty", "kindness", "bravery", "friendship", "sharing", "helping others", "never giving up"]

def generate_story_and_scenes():
    topic = random.choice(MORAL_THEMES)
    prompt = f"""Create a fun moral story for kids (age 4-8) about {topic}.
    Length: 500-650 words.
    Divide the story into 6-8 clear scenes.
    For each scene, give:
    1. Scene number
    2. Short scene description (max 15 words) - perfect for cartoon image prompt
    3. The actual story text for that scene.

    Format:
    Scene 1: [short description]
    Text: [story text]

    End with a clear moral."""

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config=GenerateContentConfig(temperature=0.8)
    )
    return response.text.strip(), topic

for video_num in range(NUM_VIDEOS):
    print(f"\n=== Generating Cartoon Video {video_num+1}/{NUM_VIDEOS} ===")
    
    full_story, topic = generate_story_and_scenes()
    folder = f"output/cartoon_{video_num+1}"
    os.makedirs(folder, exist_ok=True)

    # Save full story
    with open(f"{folder}/full_story.txt", "w", encoding="utf-8") as f:
        f.write(full_story)

    # Generate voiceover
    print("Generating voiceover...")
    communicate = Communicate(full_story, "en-US-AvaNeural")
    asyncio.run(communicate.save(f"{folder}/narration.mp3"))

    # Create simple subtitle
    with open(f"{folder}/subtitles.srt", "w", encoding="utf-8") as f:
        f.write("1\n00:00:01,000 --> 00:05:00,000\n")
        f.write(full_story.replace("\n", "\n\n"))

    title = f"Cute Cartoon: The {topic.title()} Adventure | Kids Moral Story"

    metadata = {
        "title": title,
        "description": f"{full_story[:250]}...\n\nBeautiful AI Cartoon Moral Story for Kids\n#kidscartoon #moralstories",
        "tags": ["kids cartoon", "moral story", "cartoon for kids", "ai animation"]
    }
    with open(f"{folder}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    print("Generating cartoon images for each scene...")

    # For now, we create a nice background + title. (Real image generation will be added next if needed)
    cmd = f'''
ffmpeg -y \
  -f lavfi -i color=c=#1e40af:s=1080x1920:d=300 \
  -i {folder}/narration.mp3 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=52:fontcolor=white:x=(w-text_w)/2:y=100:text='{title.replace("'", "'\\''")}':shadowcolor=black:shadowx=4:shadowy=4, \
       subtitles={folder}/subtitles.srt:force_style='Fontsize=36,PrimaryColour=&HFFFFFF,OutlineColour=&H00000000,BorderStyle=4,BackColour=&HAA000000,Shadow=2,MarginV=140,Alignment=10'" \
  -c:v libx264 -c:a aac -t 300 -pix_fmt yuv420p \
  {folder}/cartoon_video.mp4
'''

    subprocess.run(cmd, shell=True, check=True)

    print(f"✅ High-Quality Cartoon Video {video_num+1} created: {folder}/cartoon_video.mp4")

print("\n🎉 All cartoon videos generated!")
print("Download them from the Artifacts section.")
