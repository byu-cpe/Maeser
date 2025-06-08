# This script will download all transcripts from the Game Maker's Toolkit YouTube series.
# For this script to work, you must have the list of all GMTK videos downloaded as `playlist.html`
# To do this simply navigate to the GMTK playlist (https://www.youtube.com/playlist?list=PLc38fcMFcV_s7Lf6xbeRfWYRt7-Vmi_X9),
#   scroll down until all the videos have loaded, and save the page to your computer.

from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from get_yt_transcript import get_transcript_text

FILE_OUT_DIR = "transcripts"

# Parse html from playlist.html
with open("playlist.html", "r") as f:
    html_text = "".join(f.readlines())
    html = BeautifulSoup(html_text, "html.parser")

# Get each video link and extract name and id
videos = []
for playlist_video in html.find_all("ytd-playlist-video-renderer"):
    # Title
    title:str = playlist_video.find("a", id="video-title").text
    title = title.strip()

    # ID
    link = playlist_video.find("a").get("href")
    parsed = urlparse(link)
    qs = parse_qs(parsed.query)
    video_id = qs["v"][0]

    video_data = {
        "title" : title,
        "id" : video_id,
    }
    videos.append(video_data)

# Write each video transcript to separate file
failed_videos = []
for i in range(len(videos)):
    video = videos[i]
    print(f"{video["title"]} ({video["id"]})")
    try:
        transcript = get_transcript_text(video["id"])
    except Exception:
        failed_video = f"{video["title"]} ({video["id"]})"
        print(f"\033[0;33mWARNING: A video transcript failed to fetch: {failed_video}\033[0m")
        failed_videos.append(failed_video)
    else:
        filename = f"{len(videos) - i}_{video["title"].replace(" ", "_")}.txt"
        with open(f"{FILE_OUT_DIR}/{filename}", "w") as f:
            f.write(transcript)

print(f"Transcript process completed with {len(failed_videos)} failures:")
print("\n".join(failed_videos))
    