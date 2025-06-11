# This uses yt-dlp, a more feature-rich library than youtube-transcript-api. Use this if youtube-transcript-api is having issues

from yt_dlp import YoutubeDL
import json

class SubtitlesNotFoundError(Exception):
    """Raised when no subtitles are retrieved from a video."""
    pass


def get_transcript_text(video_id: str) -> str:
    ydl_opts = {
        # don’t download the actual video
        'skip_download': True,
        # tell yt_dlp to fetch both uploaded and auto‐generated captions
        'writesubtitles': True,
        'writeautomaticsub': True,
        # request json3 format
        'subtitlesformat': 'json3',
        # limit to en and en-GB
        'subtitleslangs': ["en", "en-GB"],
        # instead of writing .json to disk, dump everything to the returned info dict
        'dump_single_json': True,

        # suppress output
        'quiet': True,
        'no_warnings': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        # extract_info from video
        info = ydl.extract_info(video_url, download=False)

        # first look for manually uploaded captions, then automatic
        subs_map = info.get('subtitles') or info.get('automatic_captions')
        # raise error if no subtitles were retrieved
        if not subs_map:
            raise SubtitlesNotFoundError(f"No subtitles were retrieved from video with id={video_id}")

        # pick the first json3 track
        track = None
        for lang in ["en", "en-GB"]:
            if lang not in subs_map:
                continue
            track = next((t for t in subs_map[lang] if t.get('ext') == 'json3'), None)
            if track:
                break
        if not track:
            raise SubtitlesNotFoundError(f"No JSON subtitles available for video with id={video_id}")
        subtitle_url = track['url']

        # fetch the SRT data over HTTP
        with ydl.urlopen(subtitle_url) as resp:
            raw = resp.read().decode('utf-8')
        
        data = json.loads(raw)

        # make sure data is formatted with events
        events = data.get("events") or data

        # Add all text to transcript
        transcript = ""
        snippet_text:str = ""
        for event in events:
            if 'segs' in event:
                snippet_text = ''.join(seg.get('utf8', seg.get('text', '')) for seg in event['segs'])
            else:
                snippet_text = event.get('utf8', event.get('text',''))
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