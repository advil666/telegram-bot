import telebot
from telebot import types
import random
import threading
import time
from translate import Translator

TOKEN = '8171454576:AAGAAmFAEQJW0pdVmSmC4mC-CEVeTLBnRI4'
bot = telebot.TeleBot(TOKEN)

user_game_state = {}  # Для игры "Угадай число"
user_waiting_for_translation = set()  # Пользователи, которые вводят слово для перевода

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Привет", "Как дела?", "Пока", "🎲 Угадай число", "⏰ Напомни мне", "🌐 Переводчик")
    bot.send_message(message.chat.id, "Привет! Выбери действие 👇", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text

    # Если пользователь вводит слово для перевода
    if user_id in user_waiting_for_translation:
        # Определяем язык (простой метод: если есть кириллица — переводим в английский)
        if any('\u0400' <= c <= '\u04FF' for c in text):
            translator = Translator(from_lang="ru", to_lang="en")
        else:
            translator = Translator(from_lang="en", to_lang="ru")

        try:
            translation = translator.translate(text)
            bot.send_message(message.chat.id, f"Перевод: {translation}")
        except Exception as e:
            bot.send_message(message.chat.id, "Извините, произошла ошибка при переводе.")
        user_waiting_for_translation.remove(user_id)
        return

    # Стандартные кнопки
    if text == "Привет":
        bot.send_message(message.chat.id, "И тебе привет! 👋")
    elif text == "Как дела?":
        bot.send_message(message.chat.id, "У меня всё отлично, а у тебя?")
    elif text == "Пока":
        bot.send_message(message.chat.id, "Пока-пока! 👋")
    elif text == "🎲 Угадай число":
        secret_number = random.randint(1, 5)
        user_game_state[user_id] = secret_number
        bot.send_message(message.chat.id, "Я загадал число от 1 до 5. Попробуй угадать!")
    elif user_id in user_game_state:
        try:
            guess = int(text)
            secret = user_game_state[user_id]
            if guess == secret:
                bot.send_message(message.chat.id, f"🎉 Угадал! Это было {secret}")
            else:
                bot.send_message(message.chat.id, f"❌ Не угадал. Я загадал {secret}")
            del user_game_state[user_id]
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введи число от 1 до 5.")
    elif text == "⏰ Напомни мне":
        bot.send_message(message.chat.id, "Окей! Напомню тебе через 10 секунд 😉")
        threading.Thread(target=reminder_timer, args=(message.chat.id,)).start()
    elif text == "🌐 Переводчик":
        bot.send_message(message.chat.id, "Отправь мне слово или фразу на русском или английском, я переведу!")
        user_waiting_for_translation.add(user_id)
    else:
        bot.send_message(message.chat.id, "Не понял... Нажми кнопку, пожалуйста!")

def reminder_timer(chat_id):
    time.sleep(10)
    bot.send_message(chat_id, "⏰ Напоминаю: пора сделать перерыв или попить воды!")

bot.polling()





