from youtube_transcript_api._api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()

def get_transcript_text(video_id: str) -> str:
    fetched_transcript = ytt_api.fetch(video_id, ["en", "en-GB"])

    transcript: str = ""

    for snippet in fetched_transcript:
        transcript += snippet.text + " "

    return transcript