import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        #logger.info(f'data - file_info.file_path : {data}')
        folder_name = file_info.file_path.split('/')[0]
        #logger.info(f'folder_name : {folder_name}')

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        #return 'ok'
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ImageProcessingBot(Bot):
    def handle_message(self, msg):
        #return 'ok'
        logger.info(f'Incoming message: {msg}')
        my_caption = msg["caption"]
        if self.is_current_msg_photo(msg):
            caption_values = ['Blur', 'Contour', 'Rotate', 'Segment', 'Salt and pepper', 'Concat']
            if my_caption not in caption_values:
                self.send_text(msg['chat']['id'], 'the caption should be one of the following: Blur, Contour, Rotate, Segment, Salt and pepper, Concat')
                logger.info('Invalid Caption')
            else:
                logger.info('.........starting to apply the filter.........')

                saved_photo_path = self.download_user_photo(msg)
                new_img = Img(saved_photo_path)
                logger.info(f'Caption: {my_caption}')
                filter_function_name = my_caption.lower()
                if hasattr(Img, filter_function_name):
                    filter_function = getattr(new_img, filter_function_name)
                    filter_function()
                    new_path = new_img.save_img()
                    self.send_photo(msg['chat']['id'], new_path)
                    self.send_text(msg['chat']['id'], f'photo filtered with: {my_caption} successfully')

                    time.sleep(0.5)
        else:
            self.send_text(msg['chat']['id'], 'please upload a photo')


