import sys

import ffmpeg
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs


def download(stream_base_url, media_types, video_info):
    ffmpeg_command = 'ffmpeg'
    ffmpeg_command += f' -i "{stream_base_url}{media_types["video"]}"'
    ffmpeg_command += f' -i "{stream_base_url}{media_types["audio"]}"'
    ffmpeg_command += f' -i "{stream_base_url}{media_types["subtitle"]}"'
    ffmpeg_command += ' -vcodec copy -acodec copy "Rapport - 12 mars 19.30.mkv"'
    video_input = ffmpeg.input(f'{stream_base_url}{media_types["video"]}')
    audio_input = ffmpeg.input(f'{stream_base_url}/{media_types["audio"]}')

    output_filename = f"F:/svt/{video_info['program_title']}/{video_info['program_title']} {video_info['episode_title']}.mkv"

    (
        ffmpeg
        .concat(video_input, audio_input, v=1, a=1)
        .output(output_filename)
        .overwrite_output()
        .run()
    )
    logger.info(f'Done {output_filename}')


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


class VideoNotFound(Exception):
    pass


def download_svt_video(url, link_text):
    logger.info(f"Download {url} {link_text}")
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    links = soup.findAll('a', href=True, text=link_text)
    if not links:
        raise VideoNotFound

    for link in soup.findAll('a', href=True, text=link_text):
        modal_id = parse_qs(urlparse(link['href']).query)['modalId'][0]
        r = requests.get(f'https://api.svt.se/video/{modal_id}').json()

        video_info = {'program_title': r['programTitle'],
                      'episode_title': r['episodeTitle']}

        for video in r['videoReferences']:
            if video['format'] == 'hls':
                video_url = video['url']
                last_pos = video_url.rfind('/')
                stream_base_url = video_url[:last_pos+1]
                media_types = get_media_types(video_url)
                download(stream_base_url, media_types, video_info)
                return

    raise VideoNotFound


if __name__ == '__main__':
    global logger
    logger = logging.getLogger("my log")
    root = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename="F:/svt/log.txt")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    if root.handlers:
        root.handlers = []

    logger.info('Start')

    videos = [{'url': 'https://svtplay.se/aktuellt', 'link_text': 'Igår 21:00'},
              {'url': 'https://svtplay.se/rapport', 'link_text': 'Igår 19:30'}]

    for video in videos:
        try:
            download_svt_video(url=video['url'], link_text=video['link_text'])
        except VideoNotFound:
            logger.error(f"Video not found")
        except:
            logger.error(f"Unexpected error {sys.exc_info()[0]}")