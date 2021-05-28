
from pytube import YouTube


def main():
    with open('tmp_aktuellt.html', 'r') as f:
        page = f.read()

    video_ids = set()
    for part in page.split('/watch?v=')[1:]:
        video_id = part.split('"')[0]
        video_id = video_id.split('&amp')[0]
        video_ids.add(video_id)

    for video_id in video_ids:
        url = f"https://youtu.be/{video_id}"
        print(f"Download {url}")
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        stream.download(output_path='F:\\downloadhelper\\aktuellt')


if __name__ == '__main__':
    main()
