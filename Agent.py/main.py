from dotenv import load_dotenv
import os
import requests
from pytrends.request import TrendReq
import feedparser
import google.generativeai as genai

# 🌐 Load API keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")

# 🤖 Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# 🔍 Get trending VLSI topics
def get_top_vlsi_trends():
    pytrends = TrendReq()
    pytrends.build_payload(['VLSI design'], timeframe='now 7-d')
    try:
        rising = pytrends.related_queries()['VLSI design']['rising']
        return rising.head(5)['query'].tolist()
    except:
        return ["VLSI Design", "Semiconductor Fabrication", "Chip Architecture"]

# 📚 Fetch latest VLSI articles
def get_latest_vlsi_articles():
    feed = feedparser.parse('https://spectrum.ieee.org/rss/semiconductors.xml')
    return [{
        "title": entry.title,
        "link": entry.link,
        "summary": entry.summary
    } for entry in feed.entries[:5]]

# ✍️ Generate LinkedIn post using Gemini
def generate_post(topic, summary):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
Write a professional LinkedIn post under 150 words:
Topic: {topic}
Summary: {summary}
Include a strong opening, 1–2 insights, and a call to action or question.
"""
    response = model.generate_content(prompt)
    return response.text.strip()

# 🖼️ Get photo or video URL from Pexels
def get_media_url(query, media_type="photo"):
    headers = {
        "Authorization": PEXELS_KEY
    }

    if media_type == "photo":
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
        response = requests.get(url, headers=headers)
        data = response.json()
        return data['photos'][0]['src']['original'] if data.get('photos') else None

    elif media_type == "video":
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
        response = requests.get(url, headers=headers)
        data = response.json()
        return data['videos'][0]['video_files'][0]['link'] if data.get('videos') else None

# 🤖 Main generator
def create_ai_generated_post(media_type="photo"):
    trends = get_top_vlsi_trends()
    articles = get_latest_vlsi_articles()

    topic = trends[0]
    article = articles[0]
    media_url = get_media_url(topic, media_type=media_type)
    post_text = generate_post(topic, article['summary'])

    return {
        "topic": topic,
        "post": post_text,
        "media_url": media_url,
        "source_link": article['link']
    }

# ▶️ Run it
if __name__ == "__main__":
    data = create_ai_generated_post(media_type="photo")  # change to "video" if you want
    print("\n🧠 Topic:", data['topic'])
    print("\n📝 Post:\n", data['post'])
    print("\n🎥 Media:", data['media_url'])
    print("\n🔗 Source:", data['source_link'])

