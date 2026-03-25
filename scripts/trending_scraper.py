import requests, json
def get_trending_topics():
    url = "https://trends.google.com/trends/api/dailytrends?geo=IN"
    headers={"User-Agent":"Mozilla/5.0"}
    data=requests.get(url,headers=headers).text[5:]
    trends=json.loads(data)
    topics=[]
    for d in trends['default']['trendingSearchesDays']:
        for t in d['trendingSearches']:
            topics.append(t['title']['query'])
    return list(set(topics))[:20]

if __name__=="__main__":
    topics=get_trending_topics()
    open("content/topics.txt","w").write("\n".join(topics))
