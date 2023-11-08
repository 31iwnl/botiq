import telebot
from telebot import types
import random
import json

botTimeWeb = telebot.TeleBot('6826576613:AAHDnmKIaGa4eyMiwjgYo3rexvxMTGBJyYM')
res = ""
# Загрузка вопросов из JSON-файла
with open('questions.json', 'r', encoding='utf-8') as file:
    all_questions = json.load(file)
    questions = random.sample(all_questions, 5)  # Выбираем 5 случайных вопросов

user_data = {}  # Словарь для хранения данных пользователя


@botTimeWeb.message_handler(commands=['start'])
def start_bot(message):
    first_mess = f"<b>{message.from_user.first_name}</b>, Привет!\nНе желаешь ли пройти тест на IQ?"
    markup = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    markup.add(button_yes)
    botTimeWeb.send_message(message.chat.id, first_mess, parse_mode='html', reply_markup=markup)


@botTimeWeb.callback_query_handler(func=lambda call: call.data == "yes")
def start_test_callback(callback_query):
    user_id = callback_query.from_user.id
    user_data[user_id] = {"current_question": 0, "correct_answers": 0}
    send_question(callback_query.message.chat.id, user_id)


def send_question(chat_id, user_id):
    current_question = user_data[user_id]["current_question"]
    if current_question < len(questions):
        question_data = questions[current_question]
        botTimeWeb.send_message(chat_id, question_data["question"])
        # Создаем клавиатуру с вариантами ответов
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for answer in question_data["answers"]:
            markup.add(types.KeyboardButton(answer))
        botTimeWeb.send_message(chat_id, "Выберите вариант ответа:", reply_markup=markup)
    else:
        calculate_and_send_result(chat_id, user_id)


@botTimeWeb.message_handler(func=lambda message: True)
def check_answer(message):
    user_id = message.from_user.id
    current_question = user_data[user_id]["current_question"]
    if current_question < len(questions):
        question_data = questions[current_question]
        user_answer = message.text
        if user_answer.lower() == question_data["correct_answer"].lower():
            user_data[user_id]["correct_answers"] += 1
        user_data[user_id]["current_question"] += 1
        send_question(message.chat.id, user_id)


def calculate_and_send_result(chat_id, user_id):
    global res
    correct_answers = user_data[user_id]["correct_answers"]
    total_questions = 5  # Ограничение до 5 вопросов
    iq = (correct_answers / total_questions) * 100  # Вычисление IQ в процентах
    result_message = f"Вы ответили на: {iq:.2f} ({correct_answers}/{total_questions} % правильных ответов)."
    if (correct_answers / total_questions) * 100 < 50:
        res = "Вы глупый"
    elif 50 < (correct_answers / total_questions) * 100 < 70:
        res = "Вы нормальный"
    elif 70 < (correct_answers / total_questions) * 100 < 90:
        res = "Вы умный"
    elif (correct_answers / total_questions) * 100 > 90:
        res = "Вы гений!"
    result_message = result_message + "\n" + res
    botTimeWeb.send_message(chat_id, result_message)
    user_data.pop(user_id, None)


botTimeWeb.infinity_polling()
