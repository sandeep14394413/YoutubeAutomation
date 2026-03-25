import random, uuid
hooks=[
"You’re wasting time on {topic}…",
"Nobody tells you this about {topic}",
"Top 3 secrets about {topic}",
"Stop doing this in {topic}!",
"99% people don’t know this about {topic}"
]
topics=open("content/topics.txt").read().splitlines()
topic=random.choice(topics)
hook=random.choice(hooks).format(topic=topic)+" "+str(uuid.uuid4())[:6]
open("content/hook.txt","w").write(hook)
