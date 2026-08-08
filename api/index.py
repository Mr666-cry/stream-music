from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
import yt_dlp

app = FastAPI(title="YTMusic Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ytmusic = YTMusic()

@app.get("/")
def home():
    return {"status": "online", "message": "YTMusic API Microservice Ready!"}

@app.get("/search")
def search_songs(q: str = Query(..., description="Kata kunci lagu")):
    try:
        results = ytmusic.search(q, filter="songs")
        return {"status": "success", "query": q, "data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/stream/{video_id}")
def get_audio_stream(video_id: str):
    """Mengekstrak direct audio link dengan konfigurasi yt-dlp yang dioptimalkan untuk serverless"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info.get('url')
            
            return {
                "status": "success",
                "video_id": video_id,
                "title": info.get('title'),
                "stream_url": audio_url,
                "duration": info.get('duration')
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
