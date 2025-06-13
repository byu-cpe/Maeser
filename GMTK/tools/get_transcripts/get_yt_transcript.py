from youtube_transcript_api._api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()

def get_transcript_text(video_id: str) -> str:
    fetched_transcript = ytt_api.fetch(video_id, ["en", "en-GB"])

    transcript: str = ""

    for snippet in fetched_transcript:
        snippet_text = snippet.text
        snippet_text = snippet_text.replace('\xa0',' ').replace('\n','').strip() # remove special break characters
        transcript += snippet_text + " "
    transcript = transcript.strip()

    return transcript

if __name__ == "__main__":
    """
    For testing
    """
    test_id = "" # eg: e4vsgC41bYg
    transcript = get_transcript_text(test_id)
    # transcript = ytt_api.fetch(test_id)
    print(transcript)