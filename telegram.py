import telebot
from io import BytesIO
from PIL import Image, ImageFilter
from utils import prepare_watermark, merge_watermark

bot = telebot.TeleBot("5782503867:AAEjczM2xFkFjs3vy9QV6r-vv90UcWF7ShQ")
photo = b''


@bot.message_handler(commands=['start'])
def start(message):
    if message.text == '/start':
        bot.reply_to(message, "Add photo")


@bot.message_handler(content_types=["photo", "document"])
def get_filter(message):
    print(message)
    if message.content_type == 'document':
        file_id = message.document.file_id
    elif message.content_type == "photo":
        file_id = message.photo[-1].file_id
    else:
        return
    global photo
    file_info = bot.get_file(file_id)
    photo = bot.download_file(file_info.file_path)
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=8)
    keyboard.row(
        telebot.types.InlineKeyboardButton('Sharp', callback_data='get-sharp'),
        telebot.types.InlineKeyboardButton('Smooth', callback_data='get-smooth'),
        telebot.types.InlineKeyboardButton('Blur', callback_data='get-blur')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Gray', callback_data='get-gray'),
        telebot.types.InlineKeyboardButton('Find Edges', callback_data='get-edges')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Red', callback_data='get-red'),
        telebot.types.InlineKeyboardButton('Blue', callback_data='get-blue'),
        telebot.types.InlineKeyboardButton('Green', callback_data='get-green'),
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('Watermark', callback_data='get-watermark'),
    )
    bot.send_message(message.chat.id, "Select filter", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda query: query.data == "get-sharp")
def filter_handler(call):
    img = Image.open(BytesIO(photo))
    img = img.filter(ImageFilter.SHARPEN)
    bot.send_photo(call.from_user.id, img)


@bot.callback_query_handler(func=lambda query: query.data == "get-smooth")
def filter_handler(call):
    img = Image.open(BytesIO(photo))
    img = img.filter(ImageFilter.SMOOTH_MORE)
    bot.send_photo(call.from_user.id, img)


@bot.callback_query_handler(func=lambda query: query.data == "get-gray")
def filter_handler(call):
    img = Image.open(BytesIO(photo))
    img = img.convert("L")
    bot.send_photo(call.from_user.id, img)


@bot.callback_query_handler(func=lambda query: query.data == "get-edges")
def filter_handler(call):
    img = Image.open(BytesIO(photo))
    img = img.convert("L").filter(ImageFilter.SMOOTH).filter(ImageFilter.FIND_EDGES)
    bot.send_photo(call.from_user.id, img)


@bot.callback_query_handler(func=lambda query: query.data == "get-red")
def filter_handler(call):
    img = Image.open(BytesIO(photo))
    red, green, blue = img.split()
    zeroed_band = red.point(lambda _: 0)
    img = Image.merge("RGB", (red, zeroed_band, zeroed_band))
    bot.send_photo(call.from_user.id, img)


@bot.callback_query_handler(func=lambda query: query.data == "get-blue")
def filter_handler(call):
    img = Image.open(BytesIO(photo))
    red, green, blue = img.split()
    zeroed_band = red.point(lambda _: 0)
    img = Image.merge("RGB", (zeroed_band, zeroed_band, blue))
    bot.send_photo(call.from_user.id, img)


@bot.callback_query_handler(func=lambda query: query.data == "get-green")
def filter_handler(call):
    img = Image.open(BytesIO(photo))
    red, green, blue = img.split()
    zeroed_band = red.point(lambda _: 0)
    img = Image.merge("RGB", (zeroed_band, green, zeroed_band))
    bot.send_photo(call.from_user.id, img)


@bot.callback_query_handler(func=lambda query: query.data == "get-blur")
def filter_handler(call):
    img = Image.open(BytesIO(photo))
    img = img.filter(ImageFilter.GaussianBlur)
    bot.send_photo(call.from_user.id, img)


@bot.callback_query_handler(func=lambda query: query.data == "get-watermark")
def filter_handler(call):
    msg = bot.send_message(call.from_user.id, "Add watermark")
    bot.register_next_step_handler(msg, watermark_handler)


def watermark_handler(msg):
    if msg.content_type == 'document':
        file_id = msg.document.file_id
    elif msg.content_type == "photo":
        file_id = msg.photo[-1].file_id
    else:
        return
    file_info = bot.get_file(file_id)
    watermark_file = bot.download_file(file_info.file_path)
    img = Image.open(BytesIO(photo))
    watermark = Image.open(BytesIO(watermark_file))
    watermark = prepare_watermark(watermark)
    bot.send_photo(msg.chat.id, merge_watermark(img, watermark))


if __name__ == '__main__':
    bot.infinity_polling()
