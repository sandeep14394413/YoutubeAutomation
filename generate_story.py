import os
import json
import asyncio
import subprocess
import random
from edge_tts import Communicate
import google.genai as genai
from google.genai.types import GenerateContentConfig

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MORAL_THEMES = [
    "honesty and friendship", "kindness and sharing", "helping others", 
    "never giving up", "being brave", "respecting elders", "teamwork",
    "forgiveness", "gratitude", "caring for animals"
]

def generate_random_story():
    topic = random.choice(MORAL_THEMES)
    prompt = f"""Write a complete, fun, engaging moral story for kids (age 4-8) about {topic}.
    Length: 500-700 words. Clear beginning, middle, end. Use simple language, lots of dialogue, and vivid descriptions suitable for cartoon animation.
    End with a clear moral lesson."""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=GenerateContentConfig(temperature=0.8)
    )
    return response.text.strip(), topic

# Generate multiple videos (change number as needed)
NUM_VIDEOS = 3   # Set how many random videos you want in one run

for i in range(NUM_VIDEOS):
    print(f"\n=== Generating Video {i+1}/{NUM_VIDEOS} ===")
    story_text, topic = generate_random_story()
    
    folder = f"output/video_{i+1}"
    os.makedirs(folder, exist_ok=True)
    
    with open(f"{folder}/story.txt", "w", encoding="utf-8") as f:
        f.write(story_text)
    
    # Voiceover
    voice = "en-US-AvaNeural" if i % 2 == 0 else "en-GB-SoniaNeural"
    communicate = Communicate(story_text, voice)
    asyncio.run(communicate.save(f"{folder}/narration.mp3"))
    
    title = f"Amazing Moral Story: The Brave {topic.title()} | Kids Cartoon"
    
    metadata = {
        "title": title,
        "description": f"{story_text[:300]}...\n\nCute AI Cartoon Moral Story for Kids\n#kidsstories #moralstories #cartoonforkids",
        "tags": ["kids cartoon", "moral story", "bedtime story", "children animation", "ai story"]
    }
    with open(f"{folder}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    
    print(f"Video {i+1} story and audio ready!")

print("All videos prepared! Now you can add image generation + FFmpeg assembly in next step.")
