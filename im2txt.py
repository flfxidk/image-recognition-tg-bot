import telebot
from PIL import Image
import pytesseract
import gspread
from google.oauth2.service_account import Credentials

# Устанавливаем путь до Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Указываем путь к файлу с учетными данными
credentials_file = 'C:\\melodic-bearing-420516-d29b28092b38.json'

# Устанавливаем учетные данные для доступа к Google Sheets API
credentials = Credentials.from_service_account_file(credentials_file)
scoped_credentials = credentials.with_scopes(['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
client = gspread.Client(auth=scoped_credentials)

# Указываем ID вашей таблицы Google Sheets
spreadsheet_id = '1wBfU5w-BzUox0BQx4INU09uhCLYFRgHo6SuqK2z9_Mw'

# Устанавливаем токен бота
TOKEN = "6837678773:AAGOj8Qx55sV5wv_x19wDhkCZyCM6jeGWXI"

# Создаем объект бота
bot = telebot.TeleBot(TOKEN)

# Функция для внесения текста в Google Sheets
def update_google_sheets(text):
    try:
        # Открываем таблицу
        sheet = client.open_by_key(spreadsheet_id).sheet1
        # Вставляем текст в первую свободную ячейку
        sheet.append_row([text])
        return True
    except Exception as e:
        print(e)
        return False

# Функция для обработки команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне документ и я внесу его в Google Sheets")

# Функция для обработки изображений с текстом
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Получаем информацию о файле
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        # Загружаем изображение
        downloaded_file = bot.download_file(file_path)
        with open("image.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)

        # Открываем изображение с помощью Pillow
        image = Image.open("image.jpg")

        # Распознаем текст с помощью Tesseract
        text = pytesseract.image_to_string(image, lang='rus+eng')

        # Отправляем распознанный текст обратно в чат
        bot.reply_to(message, f"Распознанный текст:\n{text}")

        # Вносим распознанный текст в Google Sheets
        update_google_sheets(text)

    except Exception as e:
        print(e)
        bot.reply_to(message, "Что-то пошло не так. Попробуйте еще раз.")

# Запускаем бота
bot.polling()
