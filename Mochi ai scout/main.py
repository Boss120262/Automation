import feedparser
import requests
from google import genai
import json
import os

# --- Config ---
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
USER_ID = os.getenv('USER_ID')

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set in environment. "
        "Please check your local .env file or GitHub Actions secrets.GEMINI_API_KEY."
    )

def summarize_with_gemini(news_text):
    print("> กำลังส่งข่าวให้ Gemini สรุปด้วย Key ใหม่...")
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-flash-latest", 
            contents=f"คุณคือ 'โมจิ' ผู้ช่วย AI สรุปข่าว AI ต่อไปนี้เป็นภาษาไทยสั้นๆ 1-2 ประโยคต่อข่าว โดยเน้นประเด็นสำคัญและพูดจาอ่อนโยน:\n\n{news_text}"
        )
        if response.text:
            print("> [สำเร็จ!] Gemini สรุปเรียบร้อย")
            return response.text
    except Exception as e:
        print(f"> ระบบขัดข้อง: {e}")
        return None

def send_to_line(message):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    payload = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": f"🌸 [Mochi AI News Update]\n\n{message}"}]
    }
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    if res.status_code == 200:
        print("> [สำเร็จ!] ข่าวเด้งเข้า LINE บอสแล้วค่ะ!")
    else:
        print(f"> ส่ง LINE ไม่สำเร็จ: {res.status_code} {res.text}")

def track_ai_news():
    print("> เริ่มต้นดึงข่าวจาก RSS...")
    url = 'https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en'
    feed = feedparser.parse(url)
    
    if not feed.entries:
        print("> ดึงข่าวไม่ได้เลย")
        return

    print(f"> เจอข่าวทั้งหมด {len(feed.entries)} ข่าว กำลังเลือก 3 ข่าวแรก...")
    all_news = ""
    for entry in feed.entries[:3]:
        all_news += f"- {entry.title}\n"
        
    thai_summary = summarize_with_gemini(all_news)
    
    if thai_summary:
        print(f"> สรุปได้ความว่า: {thai_summary[:50]}...")
        send_to_line(thai_summary)
    else:
        print("> สรุปไม่ได้ เลยไม่ได้ส่ง LINE ")

if __name__ == "__main__":
    print("--- [ Mochi AI Scout v3.0 Start ] ---")
    track_ai_news()
    print("--- [ Finish ] ---")