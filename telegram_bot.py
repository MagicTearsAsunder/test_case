import os
import io
import logging
import face_recognition as fr
from sqlalchemy.orm import sessionmaker
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from models import engine, UsersTable, UserPicture, UserVoice
import convert_voice


base_directory = os.getcwd()
media_dir = os.path.join(base_directory, 'converted_audio')

if not os.path.exists(media_dir):
    os.mkdir(media_dir)

Session = sessionmaker(bind=engine)
session = Session()


def create_new_user(id, username):
    queue = session.query(UsersTable.the_id).filter(
        UsersTable.the_id == id
    )

    if queue.count() == 0:
        add_user = UsersTable(
            the_id=id,
            username=username
        )

        session.add(add_user)
        session.commit()

        user_dir = os.path.join(media_dir, str(id))
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)


def start(update, context):
    text = """
        Send picture. If it has human face - it would be saved.
        Send voice message. It would be saved and converted to .wav with
        16kHZ sample rate.
        """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )


def voice_handler(update, context):
    id = update._effective_user['id']
    username = update._effective_user['username']

    voice_message = update.message.voice.get_file().download_as_bytearray()

    create_new_user(id=id, username=username)

    add_voice = UserVoice(
        user_id=id,
        voice=voice_message
    )
    session.add(add_voice)
    session.commit()

    convert_voice.convert_voice(
        id, voice_message, update.message.voice['mime_type']
    )


def echo(update, context):
    id = update._effective_user['id']
    username = update._effective_user['username']

    picture = update.message.photo[-1].get_file().download_as_bytearray()

    stream = io.BytesIO()
    stream.write(picture)
    stream.name = 'photo.jpg'
    stream.seek(0)
    image = fr.load_image_file(stream)
    stream.close()

    face_locs = fr.face_locations(image)

    if face_locs:
        text = 'This picture has human face. It would be saved.'

        create_new_user(id=id, username=username)

        add_picture = UserPicture(
            user_id=id,
            picture=picture
        )
        session.add(add_picture)
        session.commit()
    else:
        text = 'This picture has no human face'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # TODO
    token = "YOUR TOKEN"
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.photo, echo))
    dispatcher.add_handler(MessageHandler(Filters.voice, voice_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
