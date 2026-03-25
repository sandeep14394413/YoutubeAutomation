import os
import json
import google.generativeai as genai
from edge_tts import Communicate
import subprocess
import asyncio
from config import STORY_PROMPT, VOICE, VIDEO_DURATION, VIDEO_WIDTH, VIDEO_HEIGHT

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

topic = "honesty and friendship"
prompt = STORY_PROMPT.format(topic=topic)

print("Generating story...")
response = model.generate_content(prompt)
story_text = response.text.strip()

print("Story generated!")

os.makedirs("output", exist_ok=True)

with open("output/story_text.txt", "w", encoding="utf-8") as f:
    f.write(story_text)

print("Generating voiceover...")
communicate = Communicate(story_text, VOICE)
audio_file = "output/narration.mp3"
asyncio.run(communicate.save(audio_file))

print("Creating video with FFmpeg...")
title = f"The Honest Little Rabbit | Moral Story for Kids"

metadata = {
    "title": title,
    "description": f"{story_text[:250]}...\n\nAI Generated Moral Story for Kids\n#kidsstories #moralstories #storytime",
    "tags": ["kids story", "moral story", "bedtime story", "ai story", "storytime"]
}

with open("output/metadata.json", "w") as f:
    json.dump(metadata, f, indent=4)

cmd = f'''
ffmpeg -y -f lavfi -i color=c=black:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:d={VIDEO_DURATION} \
-i {audio_file} \
-vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=180:text='{title.replace("'", "'\\''")}',drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:fontsize=32:fontcolor=white:x=(w-text_w)/2:y=h/2:text='{story_text.replace("'", "'\\''")[:700]}'" \
-c:v libx264 -c:a aac -t {VIDEO_DURATION} -pix_fmt yuv420p output/story_video.mp4
'''

subprocess.run(cmd, shell=True, check=True)
print("✅ Video created successfully!")