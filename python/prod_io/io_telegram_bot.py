import config
import telebot
import io_file_operation
import io_db
import os
import json
import pandas
import datetime
import re


# ---= КЛАСС ДЛЯ УПРАВЛЕНИЯ ЛОГАМИ =---
class LogManager:
    def __init__(self, logs_folder_path, logs_file_name):
        self.logs_folder_path = logs_folder_path
        self.logs_file_name = os.path.join(logs_folder_path, logs_file_name)
        self.logs = self._initialize_logs()

    def _initialize_logs(self):
        if not os.path.exists(self.logs_folder_path):
            os.makedirs(self.logs_folder_path)
        if not os.path.exists(self.logs_file_name):
            logs = pandas.DataFrame(columns=['request_time', 'chat_id', 'user_name', 'request_text', 'response_time', 'response_text', 'used_files', 'rating'])
            logs.to_csv(self.logs_file_name, index=False, encoding='utf-8')
            return logs    
        # Если файл существует, читаем его    
        try:
            return pandas.read_csv(self.logs_file_name, encoding='utf-8')
        except Exception as e:
            print(f"Ошибка при чтении логов: {e}")
            return pandas.DataFrame(columns=['request_time', 'chat_id', 'user_name', 'request_text', 'response_time', 'response_text', 'used_files', 'rating'])
        
    def log_rating(self, chat_id, rating):
        # Убедимся, что колонка rating имеет тип object
        if 'rating' in self.logs.columns and self.logs['rating'].dtype != 'object':
            self.logs['rating'] = self.logs['rating'].astype('object')

        # Обновляем запись в логах, по соответствующему chat_id
        if not self.logs.empty:
            # Находим последнюю запись в логах для этого chat_id
            self.logs.loc[self.logs['chat_id'] == chat_id, 'rating'] = rating
            print(f'[DEBUG] Оценка сохранена: {rating}')
        else:
            print(f'[DEBUG] Логи пусты, оценка не записана')
            
        # Сохраняем логи
        try:
            self.logs.to_csv(self.logs_file_name, index=False, encoding='UTF-8')
        except Exception as e:
            print(f'Ошибка при сохранении логов: {e}')

    def log_interaction(self, request_time, chat_id, user_name, request_text, response_time, response_text, used_files_path, rating=None):
        used_files_str = ", ".join(os.listdir(used_files_path)) if os.path.exists(used_files_path) else "Папка не создана"
        print(f'[DEBUG] Список файлов для логов: {used_files_str}')
        # Создаем запись логов
        new_array = pandas.DataFrame([{
            'request_time'  : request_time,
            'chat_id'       : chat_id,
            'user_name'     : user_name,
            'request_text'  : request_text,
            'response_time' : response_time,
            'response_text' : response_text,
            'used_files'    : used_files_str,
            'rating'        : rating
        }])

        if self.logs.empty:
            self.logs = new_array
        else:
            self.logs = pandas.concat([self.logs, new_array], ignore_index=True)

        try:
            self.logs.to_csv(self.logs_file_name, index=False, encoding='utf-8')
        except Exception as e:
            print(f'Ошибка при создании логов: {e}')

# ---= ИНИЦИАЛИЗАЦИЯ БОТА =---
with open ('config.json', 'r') as config_file:
    config_data = json.load(config_file)

logs_folder_path = config_data.get('logs_folder_path')
logs_manager = LogManager(logs_folder_path, 'bot_logs.csv')
bot = telebot.TeleBot(config.bot_token)

HELP_BUTTON = 'Помощь'
FILES_LIST_BUTTON = 'Загруженные файлы'
DELETE_FILES_BUTTON = 'Удалить все загруженные файлы'

# ---= ОБРАБОТКА КОМАНД =---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    io_file_operation.create_user(chat_id, username)

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        telebot.types.KeyboardButton(text=HELP_BUTTON),
        telebot.types.KeyboardButton(text=FILES_LIST_BUTTON),
        telebot.types.KeyboardButton(text=DELETE_FILES_BUTTON),
    )

    bot.send_message(message.chat.id,
        f"""Привет, {first_name}! Я бот помощник. Я помогу тебе найти нужный ответ
        Отправь мне файлы в формате PDF и задавай по ним вопросы
        Если у тебя будут предложения обращайся в Клуб Разработчиков 1С ПРО Консалтинг \n\n"""
        , reply_markup=keyboard
    )

@bot.message_handler(commands=['help'])
def help_bot(message):
    chat_id = str(message.chat.id)
    username = message.from_user.username
    io_file_operation.create_user(chat_id, username)
    bot.send_message(message.chat.id, 
        f'Вот что я умею:\n\n'
        f'1️⃣  {FILES_LIST_BUTTON} - позволяет получить перечень загруженных файлов\n'
        f'2️⃣  {DELETE_FILES_BUTTON} - выполняет полное удаление всех загруженных ранее файлов'
    )

# ---= ОБРАБОТКА ТЕКСТОВЫХ КОМАНД =---
@bot.message_handler(content_types=['text'])
def handle_buttons(message):
    text = message.text
    chatID = message.chat.id
    username = message.from_user.username
    io_file_operation.create_user(chatID, username)
    request_time = datetime.datetime.now()
    input_user_files = io_file_operation.return_user_folder_input(username)
    
    if text.startswith ('$'):
        try:
            match = re.match(r'\$(\d+)\s(.+)', text)
            if not match:
                bot.send_message(chatID, 'Ошибка в формате команды. Используйте: $<userID> <запрос>')
                return
            
            substitution_user_id = match.group(1) # user_id другого пользователя
            substitution_query =  match.group(2) # Запрос, который задаем от другого пользователя

            # Обрабатываем запрос от другого пользователя
            db_helper = io_db.DbHelper(chat_id=substitution_user_id, user_name=substitution_user_id)
            answer = db_helper.get_answer(prompt=substitution_query)

            response_text = f'Запрос от имени пользователя: {substitution_user_id}: \n {substitution_query}\n\Ответ: {answer}'
            bot.send_message(chatID, response_text)
        except Exception as e:
            bot.send_message(chatID, f'Произошла ошибка: {e}')
            print(f'Ошибка в обработке от имени другого пользователя: {e}')
        return
        
    elif text == HELP_BUTTON:    
        help_bot(message)
    elif text == FILES_LIST_BUTTON:
        io_file_operation.get_list_files(chatID, username)
    elif text == DELETE_FILES_BUTTON:
        io_file_operation.delete_all_files(chatID, username)
    else:
        if text == "":
            response_text = (chatID, 'Извините, необходимо указать запрос!')
            bot.send_message(chatID, response_text)
        elif text.startswith ('.'):
            bot.send_message(chatID, 'Запрос не по текстам, необходимо немного времени на подготовку ответа')
            db_helper = io_db.DbHelper(chat_id=chatID, user_name=username)
            response_text = db_helper.get_free_answer(prompt=text)
            bot.send_message(chatID, response_text)
        else:
            bot.send_message (chatID, 'Запрос к загруженным текстам, необходимо немного времени на подготовку ответа')
            try:
                db_helper = io_db.DbHelper(chat_id=chatID, user_name=username)
                answer = db_helper.get_answer(prompt=text)
                if answer:
                    response_text = f'Ответ: {answer}\n\n Пожалуйста, оцените качество ответа:'

                    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
                    keyboard.add(
                        telebot.types.InlineKeyboardButton('👍', callback_data=f'rate_{chatID}_up'),
                        telebot.types.InlineKeyboardButton('👎', callback_data=f'rate_{chatID}_down')
                    )
                    bot.send_message(chatID, response_text, reply_markup=keyboard)
                else:
                    response_text = 'Извините, я не смог сформировать ответ!'
                    bot.send_message(chatID, response_text)
            except Exception as e:
                response_text = 'Произошла ошибка при обработке запроса.'
                bot.send_message(chatID, response_text)
                print(f'Ошибка в get_answer: {e}')
    
    #Логируем действия
        logs_manager.log_interaction(
            request_time    =request_time,
            chat_id         =chatID,
            user_name       =username,
            request_text    =text,
            response_time   =datetime.datetime.now(),
            response_text   =response_text,
            used_files_path =input_user_files,
            rating          =None
    )

# ---= ОБРАБОТКА ДОКУМЕТОВ =---
@bot.message_handler(content_types=['document'])
def handle_document(message):
    chatID = message.chat.id
    username = message.from_user.username
    io_file_operation.create_user(chatID, username)
    file_info = bot.get_file(message.document.file_id)
    file_name = message.document.file_name

    dowloaded_file = bot.download_file(file_info.file_path)
    user_input_folder = io_file_operation.return_user_folder_input(username)
    save_path = os.path.join(user_input_folder, file_name)
    
    with open(save_path, 'wb') as new_file:
        new_file.write(dowloaded_file)

    io_file_operation.process_files(chatID, username)

    bot.send_message(chatID, f"Файл '{file_name}' успешно загружен и обработан")

# ---= ОБРАБОТКА НЕПОДДЕРЖИВАЕМЫХ ДОКУМЕТОВ =---
@bot.message_handler(content_types=['photo', 'audio', 'video', 'voice', 'sticker', 'animation', 'video_note'])
def handle_unsupported_files(message):
    bot.send_message(message.chat.id, "Извините, я обрабатываю только текстовые документы (например PDF, TXT или DOC). Пожалуйста, отправьте корректный формат файла")

# ---= ОБРАБОТКА ОЦЕНКИ ОТВЕТОВ =---
@bot.callback_query_handler(func=lambda call: call.data.startswith('rate_'))
def handle_rating(call):
    # Получаем данные из callback_data
    _, chat_id, rating = call.data.split('_')  #Например, rate_12321321_up
    chat_id = int(chat_id)
    rating_value = '👍' if rating == 'up' else '👎'

    logs_manager.log_rating(chat_id=chat_id, rating=rating_value)

    bot.answer_callback_query(call.id, f'Вы выбрали оценку:{rating_value}')

# ---= ЗАПУСК БОТА =---
try:
    print("БОТ ЗАПУЩЕН!")
    bot.polling(none_stop=True, interval=1)
except Exception as e:
    # Информация об ошибке 
    print(f"Ошибка:{e}")
finally:
    bot.stop_polling()
    print("БОТ ОСТАНОВЛЕН")