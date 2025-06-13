# IMPORTANT: YouTube has been changing its requirements recently for fetching data from its API, so it is possible that youtube-transcript-api may break.
#   If this happens, a separate implementation of `get_transcript_text` has been implemented with the yt-dlp library. It's a bit slower, but it works.
#   You can switch between the youtube-transcript-api and yt-dlp library by replacing `from get_yt_transcript` (in this script) with `from get_yt_transcript_yt_dlp` or vice versa.
# This script will download all transcripts from the Game Maker's Toolkit YouTube series.
# For this script to work, you must have the list of all GMTK videos downloaded as `playlist.html`
# To do this, simply navigate to the GMTK playlist (https://www.youtube.com/playlist?list=PLc38fcMFcV_s7Lf6xbeRfWYRt7-Vmi_X9),
#   scroll down until all the videos have loaded, and save the page to this directory as `playlist.html`.

from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from get_yt_transcript import get_transcript_text

FILE_OUT_DIR = "transcripts"

# Parse html from playlist.html
with open("playlist.html", "r") as f:
    html_text = "".join(f.readlines())
    html = BeautifulSoup(html_text, "html.parser")

# Get each video link and extract Title, ID, and Absolute Link
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

    # Absolute Link
    link_absolute = f"https://www.youtube.com{link}"

    video_data = {
        "title" : title,
        "id" : video_id,
        "link" : link_absolute,
    }
    videos.append(video_data)

# Write each video transcript to separate file
failed_videos = []
for i in range(len(videos)):
    video = videos[i]
    print(f"({len(videos) - i}/{len(videos)}) {video["title"]} ({video["id"]})")
    try:
        transcript = get_transcript_text(video["id"])
    except Exception:
        failed_video = f"{video["title"]} ({video["id"]})"
        print(f"\033[0;33mWARNING: A video transcript failed to fetch: {failed_video}\033[0m")
        failed_videos.append(failed_video)
    else:
        filename = f"{len(videos) - i}_{video["title"].replace(" ", "_")}.txt"
        url = video["link"]
        with open(f"{FILE_OUT_DIR}/{filename}", "w") as f:
            f.write(url + "\n") # Write url to top of file
            f.write(transcript) # Write transcript

num_fails = len(failed_videos)
print(f"Transcript process completed with {num_fails} failures{":" if num_fails > 0 else "."}")
print("\n".join(failed_videos))
    