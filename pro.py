from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import InlineKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os

# подгружаем переменные окружения
load_dotenv()

# токен бота
TOKEN = os.getenv('TG_TOKEN')

# Словарь для хранения выбранного языка пользователем
user_language = {}

# Словарь с сообщениями на разных языках
messages = {
    'en': {
        'language_selected': "Language selected: English",
        'text_received': "We’ve received a message from you!",
        'voice_received': "We’ve received a voice message from you!",
        'photo_saved': "Photo saved!"
    },
    'ru': {
        'language_selected': "Выбранный язык: Русский",
        'text_received': "Текстовое сообщение получено!",
        'voice_received': "Голосовое сообщение получено",
        'photo_saved': "Фотография сохранена"
    }
}

# INLINE
# форма inline клавиатуры
keyboard = [
         [InlineKeyboardButton("English", callback_data='en'),
         InlineKeyboardButton("Русский", callback_data='ru')]
]
# создаем inline клавиатуру
inline_keyboard = InlineKeyboardMarkup(keyboard)

# функция-обработчик команды /start
async def start(update: Update, _):
    # прикрепляем inline клавиатуру к сообщению
    await update.message.reply_text('Please choose your language / Пожалуйста выберите язык:', reply_markup=inline_keyboard)


# функция-обработчик нажатий на кнопки
async def button(update: Update, _):
    # получаем callback query из update
    query = update.callback_query
    # всплывающее уведомление
    await query.answer()
    user_language[query.from_user.id] = query.data
    await query.edit_message_text(text=messages[query.data]['language_selected'])


async def text(update: Update, _) -> None:
    user_id = update.message.from_user.id
    language = user_language.get(user_id, 'en')
    text = messages[language]['text_received']
    await update.message.reply_text(text)

async def voice(update: Update, _) -> None:
    user_id = update.message.from_user.id
    language = user_language.get(user_id, 'en')
    text = messages[language]['voice_received']
    await update.message.reply_photo(photo=open('DALL-E.png', 'rb'), caption=text)

async def photo(update: Update, _) -> None:
    user_id = update.message.from_user.id
    language = user_language.get(user_id, 'en')
    photo_file = await update.message.photo[-1].get_file()

    # Проверка существования папки и создание, если она отсутствует
    if not os.path.exists('photos'):
        os.makedirs('photos')

    await photo_file.download_to_drive(f'photos/photo{update.message.id}.jpg')
    text = messages[language]['photo_saved']
    await update.message.reply_text(text)

def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем CallbackQueryHandler (только для inline кнопок)
    application.add_handler(CallbackQueryHandler(button))

    application.add_handler(MessageHandler(filters.TEXT, text))

    application.add_handler(MessageHandler(filters.VOICE, voice))

    application.add_handler(MessageHandler(filters.PHOTO, photo))

    # запускаем бота (нажать Ctrl-C для остановки бота)
    application.run_polling()
    print('Бот остановлен')


if __name__ == "__main__":
    main()