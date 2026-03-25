from gtts import gTTS
text=open("content/script.txt").read()
tts=gTTS(text=text)
tts.save("output/voice.mp3")
