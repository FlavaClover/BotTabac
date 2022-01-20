from django.core.management import BaseCommand
from django.conf import settings
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
from bot.models import User, Product
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

main_keyboard = ReplyKeyboardMarkup([
    ['Показать товары'],
    ['Обновить номер телефона'],
])

menu_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('<--', callback_data='back'),
        InlineKeyboardButton('-->', callback_data='next'),
    ],
    [
        InlineKeyboardButton('В корзину', callback_data='in basket'),
    ],
    [
        InlineKeyboardButton('Показать коризну', callback_data='show backet'),
    ],
])

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
        button_query_handler = CallbackQueryHandler(button)
        start_conversation = ConversationHandler(entry_points=[start_handler],
                                                 states={
                                                     1: [MessageHandler(Filters.contact, get_contact)],
                                                 },
                                                 fallbacks=[])

        dispatcher.add_handler(start_conversation)
        dispatcher.add_handler(show_products_handler)
        dispatcher.add_handler(button_query_handler)

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


def show_products(update: Update, context: CallbackContext):
    """Command that send products"""
    context.user_data['product_number'] = 0
    product = Product.objects.all()[0]
    product_image = open("product_images/" + product.img_name + ".jpg", "rb")

    update.effective_chat.send_photo(photo=product_image, caption=product.name_external,
                                     reply_markup=menu_keyboard)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    key = f'product_number'
    product_number_current = context.user_data[key]
    products = Product.objects.all()

    if query.data == 'next':
        if product_number_current + 1 < len(products):
            context.user_data[key] += 1
    elif query.data == 'back':
        if product_number_current - 1 >= 0:
            context.user_data[key] -= 1

    product_number = context.user_data[key]
    product = Product.objects.all()[product_number]
    product_image = open(f'product_images/{product.img_name}.jpg', 'rb')

    if query.data == 'in basket':

        if 'basket' not in context.user_data:
            context.user_data['basket'] = dict()

        if product.name_internal in context.user_data['basket']:
            context.user_data['basket'][product.name_internal]['count'] += 1
        else:
            context.user_data['basket'][product.name_internal] = {'count': 1, 'product': product}

        print(context.user_data['basket'])

    query.edit_message_media(media=InputMediaPhoto(media=product_image))
    caption = product.name_external

    if 'basket' in context.user_data and product.name_internal in context.user_data['basket']:
        caption += f'({context.user_data["basket"][product.name_internal]["count"]} шт.)'

    query.edit_message_caption(caption=caption, reply_markup=menu_keyboard)