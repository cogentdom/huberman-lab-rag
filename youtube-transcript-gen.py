import os
from youtube_transcript_api import get_transcript

def get_transcript(video_id):
    transcript = get_transcript(video_id)
    return transcript

print(get_transcript("dQw4w9WgXcQ"))
