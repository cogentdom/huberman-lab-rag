# import os
# from youtube_transcript_api import get_transcript

# def get_transcript(video_id):
#     transcript = get_transcript(video_id)
#     return transcript

# print(get_transcript('https://www.youtube.com/watch?v=sxgCC4H1dl8'))


from youtube_transcript_api import YouTubeTranscriptApi



ytt_api = YouTubeTranscriptApi()

video_id = 'sxgCC4H1dl8'
filename = 'my_transcript.txt'
title = 'Adderall, Stimulants & Modafinil for ADHD: Short- & Long-Term Effects | Huberman Lab Podcast'

fetched_transcript = ytt_api.fetch(video_id)

with open(filename, 'w', encoding='utf-8') as file:
    for snippet in fetched_transcript:
        file.write(snippet.text + '\n')  # Add newline after each snippet