
from pytube import YouTube
from bs4 import BeautifulSoup


def main():
    with open('tmp_fohm_presstraff.html', 'r') as f:
        page = f.read()

    soup = BeautifulSoup(page, 'html.parser')

    videos = soup.find_all(name='a', id='video-title')

    video_ids = {}
    for video in videos:
        video_id = video['href'].replace('/watch?v=', '').split('&')[0]
        video_ids[video_id] = video['title']

    print(video_ids)

    for video_id in video_ids:
        url = f"https://youtu.be/{video_id}"
        print(f"Download {url}")
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        stream.download(output_path='F:\\downloadhelper\\fohm_presstraff')


if __name__ == '__main__':
    main()
