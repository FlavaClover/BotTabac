from django.core.management import BaseCommand
from django.conf import settings
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import Updater, CallbackContext, CommandHandler, ConversationHandler, MessageHandler, Filters
from bot.models import User
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

main_keyboard = ReplyKeyboardMarkup([['Показать товары'], ['Обновить номер телефона']])
logger = logging.getLogger()


class Command(BaseCommand):
    """Command that starting the bot"""
    help = 'Start bot'

    def handle(self, *args, **options):
        """Here bot is created and launched"""
        updater = Updater(token=settings.BOT_TOKEN)
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', start_command)
        show_products_handler = MessageHandler(Filters.regex('Показать товары'), show_products)
        start_conversation = ConversationHandler(entry_points=[start_handler],
                                                 states={
                                                     1: [MessageHandler(Filters.contact, get_contact)],
                                                 },
                                                 fallbacks=[])
        dispatcher.add_handler(start_conversation)
        dispatcher.add_handler(show_products_handler)

        updater.start_polling()


def start_command(update: Update, _: CallbackContext):
    """Start command that send greets the user and asks for thr phone number"""
    try:
        u = User.objects.get(chat_id=update.effective_chat.id)
    except User.DoesNotExist:
        u = User.objects.create(chat_id=update.effective_chat.id,
                                first_name=update.effective_user.first_name,
                                last_name=update.effective_user.last_name,
                                username=update.effective_user.username)
        u.save()
        logger.info(f'User {u} created!')

    text = f'{u.first_name}, добро пожаловать!'
    print(u.telephone)
    if not u.telephone:
        text += 'Пожалуйста, отправьте мне свой номер телефона, чтобы доставщик мог с Вами связываться.'
        keyboard_for_phone = ReplyKeyboardMarkup(resize_keyboard=True,
                                                 keyboard=[
                                                     [KeyboardButton('Отправить номер телефона', request_contact=True)]
                                                 ])

        update.effective_message.reply_text(text=text,
                                            reply_markup=keyboard_for_phone)

    if not u.telephone:
        return 1
    else:
        update.effective_message.reply_text(text=text, reply_markup=main_keyboard)
        return ConversationHandler.END


def get_contact(update: Update, _: CallbackContext):
    """Command that gets the phone number"""
    chat_id = update.effective_chat.id
    phone_number = update.effective_message.contact.phone_number

    u = User.objects.get(chat_id=chat_id)
    u.telephone = phone_number
    u.save()
    logger.info(f'User {u} set phone {u.telephone}!')

    update.effective_message.reply_text(text='Спасибо, принято!', reply_markup=main_keyboard)

    return ConversationHandler.END


def show_products(update: Update, _: CallbackContext):
    """Command that send products"""
    menu_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('<--', callback_data='back'),
            InlineKeyboardButton('-->', callback_data='next'),
        ],
        [
            InlineKeyboardButton('В корзину', callback_data='in basket'),
        ],
    ])

    update.effective_message.reply_text(text='One sec', reply_markup=menu_keyboard)