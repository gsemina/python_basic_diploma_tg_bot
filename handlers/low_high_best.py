from loader import bot
from telebot.types import Message
from loguru import logger
import datetime
from states.user_states import UserInputState
import keyboards.inline
import api_request
from keyboards.calendar.telebot_calendar import Calendar
import data_json
from utils.display_data import display_data
import database


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def low_high_best_handler(message: Message) -> None:
    """
    Реагирует на команды /lowprice, /highprice, /bestdeal
    и запоминает необходимые данные.
    Спрашивает пользователя - какой искать город.
    : param message : Message
    : return : None
    """
    bot.set_state(message.chat.id, UserInputState.command)
    with bot.retrieve_data(message.chat.id) as data:
        data.clear()
        logger.info('Запоминаем выбранную команду: ' + message.text)
        data['command'] = message.text
        data['sort'] = check_command(message.text)
        data['date_time'] = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        data['chat_id'] = message.chat.id
    database.add_users_bd.add_user(message.chat.id,
                                   message.from_user.username,
                                   message.from_user.full_name)
    bot.set_state(message.chat.id, UserInputState.input_city)
    bot.send_message(message.from_user.id, "Введите город в котором нужно найти отель: ")


@bot.message_handler(state=UserInputState.input_city)
def input_city(message: Message) -> None:
    """
    Получаем название города от пользователя и
    отправляем запрос на сервер для поиска вариантов городов.
    Генерируем клавиатуру с вариантами городов.
    : param message : Message
    : return : None
    """
    with bot.retrieve_data(message.chat.id) as data:
        data['input_city'] = message.text
        logger.info('Пользователь ввел город: ' + message.text)
        # Создаем запрос для поиска вариантов городов и генерируем клавиатуру
        url = "https://hotels4.p.rapidapi.com/locations/v3/search"
        querystring = {"q": message.text, "locale": "en_US"}
        response_cities = api_request.request.request('GET', url, querystring)
        if response_cities.status_code == 200:
            possible_cities = data_json.search_city.search_citys(response_cities.text) #возможные города из json файлов
            keyboards.inline.inline_kb.city_choice_keyboard(message, possible_cities)
        else:
            bot.send_message(message.chat.id,
                             f"Что-то пошло не так, код ошибки: {response_cities.status_code}")
            bot.send_message(message.chat.id,
                             'Нажмите команду еще раз. И введите другой город.')
            data.clear()


@bot.message_handler(state=UserInputState.quantity_hotels)
def quantity_hotels(message: Message) -> None:
    """
    Запоминаем кол-во отелей, которое выбрал пользователь.
    Проверяем корректность, и входит ли число в диапазон от 1 до 10.
    Запрашиваем минимальную стоимость отеля.
    : param message : Message
    : return : None
    """
    if message.text.isdigit():
        if 0 < int(message.text) <= 10:
            logger.info('Ввод и запись количества отелей: ' + message.text)
            with bot.retrieve_data(message.chat.id) as data:
                data['quantity_hotels'] = message.text
            bot.set_state(message.chat.id, UserInputState.priceMin)
            bot.send_message(message.chat.id, 'Введите минимальную стоимость отеля в долларах США (от 1$):')
        else:
            bot.send_message(message.chat.id,
                             'Ошибка! Это должно быть число в диапазоне от 1 до 10! Повторите ввод!')
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число! Повторите ввод!')


@bot.message_handler(state=UserInputState.priceMin)
def min_price(message: Message) -> None:
    """
    Проверяем введенную минимальную стоимость отеля, чтобы это было число.
    Записываем его в priceMin.
    Запрашиваем максимальную стоимость отеля.
    : param message : Message
    : return : None
    """
    if message.text.isdigit() > 0:
        logger.info('Ввод и запись минимальной стоимости отеля: ' + message.text)
        with bot.retrieve_data(message.chat.id) as data:
            data['price_min'] = message.text
        bot.set_state(message.chat.id, UserInputState.priceMax)
        bot.send_message(message.chat.id, 'Введите максимальную стоимость отеля в долларах США:')
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число или оно меньше 1! Повторите ввод!')


@bot.message_handler(state=UserInputState.priceMax)
def max_price(message: Message) -> None:
    """
    Проверяем введенную максимальную стоимость отеля, чтобы это было число.
    Записываем его в priceMax.
    Максимальное число не может быть меньше минимального.
    : param message : Message
    : return : None
    """
    if message.text.isdigit():
        logger.info('Ввод и запись максимальной стоимости отеля, сравнение с price_min: ' + message.text)
        with bot.retrieve_data(message.chat.id) as data:
            if int(data['price_min']) < int(message.text):
                data['price_max'] = message.text
                keyboards.inline.inline_kb.photo_selection(message)
            else:
                bot.send_message(message.chat.id,
                                 'Максимальная цена должна быть больше минимальной. Повторите ввод!')
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число! Повторите ввод!')


@bot.message_handler(state=UserInputState.photo_count)
def quantity_photo(message: Message) -> None:
    """
    Проверяем введенное кол-во фотографий пользователем на корректность
    и соответствие заданному диапазону от 1 до 10
    Записываем в photo_count
    : param message : Message
    : return : None
    """
    if message.text.isdigit():
        if 0 < int(message.text) <= 10:
            logger.info('Ввод и запись количества фотографий: ' + message.text)
            with bot.retrieve_data(message.chat.id) as data:
                data['photo_count'] = message.text
            my_calendar(message, 'заезда')
        else:
            bot.send_message(message.chat.id,
                             'Число фотографий должно быть в диапазоне от 1 до 10! Повторите ввод!')
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число! Повторите ввод!')


@bot.message_handler(state=UserInputState.start_distance_to_center)
def start_distance_to_center(message: Message) -> None:
    """
    Добавляем начало диапазона расстояния до центра,
    проверяем на корректность.
    : param message : Message
    : return : None
    """
    if message.text.isdigit():
        with bot.retrieve_data(message.chat.id) as data:
            data['start_distance_to_center'] = message.text
        bot.set_state(message.chat.id, UserInputState.end_distance_to_center)
        bot.send_message(message.chat.id, 'Введите конец диапазона расстояния от центра (в милях).')
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число! Повторите ввод!')


@bot.message_handler(state=UserInputState.end_distance_to_center)
def end_distance_to_center(message: Message) -> None:
    """
    Добавляем конец диапазона расстояния до центра,
    проверяем на корректность.
    : param message : Message
    : return : None
    """
    if message.text.isdigit():
        with bot.retrieve_data(message.chat.id) as data:
            data['end_distance_to_center'] = message.text
            display_data(message, data)
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число! Повторите ввод!')


def check_command(command: str) -> str:
    """
    Проверка команды и назначение параметра для сортировки.
    : param command : str команда, выбранная (введенная) пользователем
    : return : str команда сортировки
    """
    if command == '/bestdeal':
        return 'DISTANCE'
    elif command == '/lowprice' or command == '/highprice':
        return 'PRICE_LOW_TO_HIGH'


bot_calendar = Calendar()


def my_calendar(message: Message, word: str) -> None:
    """
    Запуск клавиатуры - календаря для выбора дат заезда и выезда
    : param message : Message
    : param word : str слово (заезда или выезда)
    : return : None
    """
    bot.send_message(message.chat.id, f'Выберите дату: {word}',
                     reply_markup=bot_calendar.create_calendar())