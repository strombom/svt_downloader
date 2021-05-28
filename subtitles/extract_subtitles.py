import os
import glob


def main():
    video_paths = [
        "F:/svt/Aktuellt",
        "F:/svt/Rapport",
        "F:/svt/Blandat"
    ]
    output_path = "F:/svt/Subtitles"

    for video_path in video_paths:
        for video_filepath in glob.glob(os.path.join(video_path, "*.mkv")):
            video_filepath = video_filepath.replace('\\', '/')
            subtitle_filename = video_filepath.split('/')[-1].replace('mkv', 'srt')
            subtitle_filepath = os.path.join(output_path, subtitle_filename)
            os.system(f"ffmpeg -i \"{video_filepath}\" -map 0:s \"{subtitle_filepath}\" -y")


if __name__ == '__main__':
    main()
