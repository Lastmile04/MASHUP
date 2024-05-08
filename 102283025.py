import os
import re
import time
import zipfile
import urllib.error
from send_mail import send_mail
import streamlit as st
from youtube_search import YoutubeSearch
from pytube import YouTube, Search, exceptions
from moviepy.editor import VideoFileClip, concatenate_audioclips

os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"

def download_video(singer, n):
    count = 0
    query = singer + ' music video'
    results = YoutubeSearch(query, max_results=n + 20).to_dict()
    for v in results:
        try:
            yt = YouTube('https://youtube.com/' + v['url_suffix'])
            video = yt.streams.filter(file_extension='mp4').first()
            destination = 'Video Files'

            for attempt in range(3):
                try:
                    out_file = video.download(output_path=destination)
                    break
                except Exception as e:
                    print(f"Error downloading video (attempt {attempt+1}): {e}")
                    time.sleep(2**attempt)  # Exponential backoff
            else:
                print("Failed to download video after multiple attempts.")
                continue

        except (exceptions.VideoUnavailable, urllib.error.HTTPError):
            pass
        else:
            count += 1
            if count == n:
                break
            basePath, extension = os.path.splitext(out_file)
    if count == 0:
        st.error(f"No videos found for {singer}")
    else:
        st.info('Downloaded Videos')


def convert_video_to_audio(output_ext="mp3"):
    directory = "Video Files/"
    clips = []
    for filename in os.listdir(directory):
        if filename.endswith(".mp4"):
            file_path = os.path.join(directory, filename)
            clip = VideoFileClip(file_path)
            audioclip = clip.audio
            basePath, extension = os.path.splitext(filename)
            clips.append(audioclip)
    st.info('Converted Videos to Audios')
    return clips


def trimAudioClips(clips, duration):
    subclips = []
    for clip in clips:
        subclip = clip.subclip(0, duration)
        subclips.append(subclip)
    st.info('Trimmed Audios')
    return subclips


def mashup(clips, output='mashup'):
    concat = concatenate_audioclips(clips)
    concat.write_audiofile(f"{output}.mp3")
    st.success('Created Mashup')


def createZip(file):
    destination = 'mashup.zip'
    zip_file = zipfile.ZipFile(destination, 'w')
    zip_file.write(file, compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()
    return destination


def script(singer, count, duration, mail, output='mashup'):
    download_video(singer, count)
    clips = convert_video_to_audio()
    subclips = trimAudioClips(clips, duration)
    mashup(subclips, output)
    send_mail(mail, createZip('mashup.mp3'))
    st.info('Mail Sent!')


st.title('Mashup Music 007')
st.subheader('by Dikshant Thakur')

with st.form("my_form"):
    st.write("Fill in the details below to generate your custom music mashup.")
    singer = st.text_input('Name of Artist')
    count = st.slider('Number of Videos', 5, 40)
    duration = st.slider('Duration of Each