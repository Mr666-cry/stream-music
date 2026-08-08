from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
import yt_dlp

app = FastAPI(title="YTMusic Microservice")

# Mengizinkan akses dari frontend manapun (CORS)
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
    """Endpoint pencarian lagu berdasarkan query"""
    try:
        results = ytmusic.search(q, filter="songs")
        return {"status": "success", "query": q, "data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/song/{video_id}")
def get_song_detail(video_id: str):
    """Endpoint mengambil detail metadata lagu"""
    try:
        song_data = ytmusic.get_song(video_id)
        return {"status": "success", "data": song_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/stream/{video_id}")
def get_audio_stream(video_id: str):
    """Endpoint mengekstrak Direct Audio Stream URL via yt-dlp"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'force_generic_extractor': False,
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

@app.get("/lyrics/{video_id}")
def get_lyrics(video_id: str):
    """Endpoint mengambil lirik lagu berdasarkan video_id"""
    try:
        watch_playlist = ytmusic.get_watch_playlist(videoId=video_id)
        lyrics_id = watch_playlist.get("lyrics")
        if not lyrics_id:
            return {"status": "error", "message": "Lirik tidak ditemukan"}
        
        lyrics_data = ytmusic.get_lyrics(lyrics_id)
        return {"status": "success", "data": lyrics_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
