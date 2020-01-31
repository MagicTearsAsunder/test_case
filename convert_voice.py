import os
import ffmpeg
import soundfile as sf
from telegram_bot import media_dir


def convert_voice(id, voice_message, mime_type):
    mime_type = mime_type.split('/')[-1]

    user_dir = os.path.join(media_dir, str(id))
    new_file_path = os.path.join(user_dir, f'new_file.{mime_type}')
    audio_file = open(new_file_path, 'wb')
    audio_file.write(voice_message)
    audio_file.close()

    stream = ffmpeg.input(new_file_path)
    counter = len(os.listdir(user_dir)) - 1
    convert_file_path = os.path.join(user_dir, f'audio_message_{counter}.wav')
    stream = ffmpeg.output(stream, convert_file_path)
    ffmpeg.run(stream)

    os.remove(new_file_path)

    data, samplerate = sf.read(convert_file_path)
    sf.write(convert_file_path, data, 16000)
