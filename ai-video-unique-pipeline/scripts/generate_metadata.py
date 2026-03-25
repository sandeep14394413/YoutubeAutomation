import json,random
script=open("content/script.txt").read()
aff=json.load(open("config/affiliate.json"))
cat=random.choice(list(aff.keys()))
prod=random.choice(aff[cat])

meta={
"title":script[:60],
"description":f"{script}\n\nBuy: {prod['link']}\n#shorts #ai"
}
json.dump(meta,open("output/metadata.json","w"))
