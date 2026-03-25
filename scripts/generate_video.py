from moviepy.editor import *
import random

audio=AudioFileClip("output/voice.mp3")
img="assets/bg.jpg"

video=ImageClip(img).set_duration(audio.duration).set_audio(audio).resize((1080,1920))
video.write_videofile("output/video.mp4",fps=24)
