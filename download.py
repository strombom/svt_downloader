
import os
import sys
import logging
import requests
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup
# from datetime import datetime
from urllib.parse import urlparse, parse_qs


def get_media_types(video_url):
    media_types = {'video': None,
                   'audio': None,
                   'subtitle': None}

    videos = []
    next_is_video = False
    for row in requests.get(video_url).text.split('\n'):
        if next_is_video:
            videos.append(row)
            next_is_video = False
            continue

        if '#EXT-X-MEDIA:TYPE=AUDIO' in row:
            for attribute in row.split(','):
                if 'URI=' in attribute:
                    media_types['audio'] = attribute.replace('"', '').replace('URI=', '')
                    break

        if '#EXT-X-MEDIA:TYPE=SUBTITLES' in row:
            for attribute in row.split(','):
                if 'URI=' in attribute:
                    media_types['subtitle'] = attribute.replace('"', '').replace('URI=', '')
                    break

        if '#EXT-X-STREAM-INF' in row:
            next_is_video = True
        else:
            next_is_video = False

    videos.sort()
    if len(videos) > 0:
        media_types['video'] = videos[-1]

    return media_types


def download(stream_base_url, media_types, video_info, output_directory):
    current_year = datetime.datetime.now().year
    output_filename = f"{output_directory}/{video_info['program_title']} {current_year}"
    try:
        os.makedirs(output_filename)
    except FileExistsError:
        pass
    output_filename += f"/{video_info['program_title']} {video_info['episode_title']}.mkv"

    ffmpeg_command = 'ffmpeg -y'
    ffmpeg_command += f' -i "{stream_base_url}{media_types["video"]}"'
    ffmpeg_command += f' -i "{stream_base_url}{media_types["audio"]}"'
    ffmpeg_command += f' -i "{stream_base_url}{media_types["subtitle"]}"'
    ffmpeg_command += f' -vcodec copy -acodec copy "{output_filename}"'

    subprocess.run(ffmpeg_command, shell=True, check=True)
    logger.info(f'Done {output_filename}')


class VideoNotFound(Exception):
    pass


def download_svt_video(url, link_text, output_directory):
    logger.info(f"Download {url} {link_text}")
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    for link in soup.find_all('a', href=lambda href: href and link_text in href):
        link_href = parse_qs(urlparse(link['href']).query)
        if 'id' not in link_href:
            continue

        modal_id = link_href['id'][0]
        r = requests.get(f'https://api.svt.se/video/{modal_id}').json()

        video_info = {'program_title': r['programTitle'],
                      'episode_title': r['episodeTitle'].replace(':', '-')}

        for video in r['videoReferences']:
            if video['format'] == 'hls':
                video_url = video['url']
                last_pos = video_url.rfind('/')
                stream_base_url = video_url[:last_pos+1]
                media_types = get_media_types(video_url)
                download(stream_base_url, media_types, video_info, output_directory)
                return

    raise VideoNotFound


if __name__ == '__main__':
    output_directory = "D:/Svt"
    try:
        os.makedirs(output_directory)
    except FileExistsError:
        pass

    global logger
    logger = logging.getLogger("my log")
    root = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename=f"{output_directory}/log.txt")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    if root.handlers:
        root.handlers = []

    logger.info('Start')

    videos = [
        {'url': 'https://svtplay.se/rapport', 'link_text': 'rapport/igar-19-30'},
        {'url': 'https://svtplay.se/aktuellt', 'link_text': 'aktuellt/igar-21-00'}
    ]

    # weekday = ('Mån', 'Tis', 'Ons', 'Tor', 'Fre', 'Lör', 'Sön')[(datetime.datetime.now().weekday() - 1) % 6]

    for video in videos:
        try:
            download_svt_video(url=video['url'], link_text=video['link_text'], output_directory=output_directory)
        except VideoNotFound:
            logger.error(f"Video not found")
        except:
            logger.error(f"Unexpected error {sys.exc_info()[0]}")
