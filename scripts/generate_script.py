import random, uuid
hook=open("content/hook.txt").read()
variations=[
"Explain in simple terms.",
"Make it exciting.",
"Add curiosity gaps.",
"Make it shocking."
]
script=f"{hook}\n\n{random.choice(variations)}\nCTA: Check link in description!"
script+=f"\nID:{uuid.uuid4()}"
open("content/script.txt","w").write(script)
