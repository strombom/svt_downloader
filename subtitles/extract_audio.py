import os
import glob


def main():
    video_paths = [
        "F:\corona\Blandat"
    ]
    output_path = "F:/corona/Blandat/audio"

    for video_path in video_paths:
        for video_filepath in glob.glob(os.path.join(video_path, "*.webm")):
            video_filepath = video_filepath.replace('\\', '/')
            audio_filename = video_filepath.split('/')[-1].replace('webm', 'aac')
            audio_filepath = os.path.join(output_path, audio_filename)
            os.system(f"ffmpeg -i \"{video_filepath}\" -map 0:a \"{audio_filepath}\" -y")


if __name__ == '__main__':
    main()
