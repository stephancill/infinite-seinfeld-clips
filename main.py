import os
import shutil
import requests
import json
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import youtube_dl
import random
import datetime

def download_twitch_clips(urls, temp_dir):
    ydl_opts = {
        "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
        # "quiet": True,
    }
    filenames = []
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            info = ydl.extract_info(url, download=False)
            filenames.append(os.path.join(temp_dir, info["title"] + "." + info["ext"]))
            print(f"Downloading {info['title']}...")
            ydl.download([url])
    return filenames

def join_videos(filenames, clip_data, output_file):
    clips = []
    for filename, clip in zip(filenames, clip_data):
        video_clip = VideoFileClip(filename)
        text_clip = TextClip(
            clip["title"] + " - " + str(clip["view_count"]),
            fontsize=24,
            color='white',
            size=video_clip.size,

        )
        
        # video_with_text = CompositeVideoClip([video_clip, text_clip.set_pos(("right", "bottom"))]).set_duration(video_clip.duration)
        # video_with_text = video_with_text
        # print(f"Duration: {video_with_text.duration} - {clip['title']}")
        clips.append(video_clip)
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_file)

def get_twitch_access_token(client_id, client_secret):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    response = requests.post("https://id.twitch.tv/oauth2/token", headers=headers, data=data)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None

def get_broadcaster_id(channel_name, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-ID": os.environ["TWITCH_CLIENT_ID"]
    }
    response = requests.get(f"https://api.twitch.tv/helix/users?login={channel_name}", headers=headers)

    if response.status_code == 200:
        data = response.json()["data"]
        if len(data) > 0:
            return data[0]["id"]
        else:
            return None
    else:
        return None

def fetch_top_clips(broadcaster_id, count, access_token):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-ID": os.environ["TWITCH_CLIENT_ID"],
    }
    params = {
        "broadcaster_id": broadcaster_id,
        "period": "day",
        "limit": 100
    }
    response = requests.get(f"https://api.twitch.tv/helix/clips", headers=headers, params=params)
    data = response.json()

    sorted_clips = sorted(data["data"], key=lambda clip: clip["view_count"], reverse=True)[:count]
    return sorted_clips

def main():
    temp_dir = "temp_dir"

    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    channel = "watchmeforever"
    count = 5

    twitch_access_token = get_twitch_access_token(os.environ["TWITCH_CLIENT_ID"], os.environ["TWITCH_CLIENT_SECRET"])

    broadcaster_id = get_broadcaster_id(channel, twitch_access_token)

    top_clips = fetch_top_clips(broadcaster_id, count, twitch_access_token)

    # Shuffle clip urls
    random.shuffle(top_clips)

    filenames = download_twitch_clips([x["url"] for x in top_clips], temp_dir)

    # Date string in format YYYY-MM-DD
    date_string = datetime.datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(temp_dir, "joined_videos.mp4")
    join_videos(filenames, top_clips, output_file)

    # Create metadata file
    with open(f"{date_string}.txt", "w") as f:
        for clip in top_clips:
            f.write(f"{clip['title']} - {clip['view_count']} views ({clip['url']})")

    shutil.copy(output_file, f"./{date_string}.mp4")
    shutil.rmtree(temp_dir)

main()
