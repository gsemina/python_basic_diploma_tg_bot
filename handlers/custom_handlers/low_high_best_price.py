from datetime import datetime

from loguru import logger
from telebot import types

from api_request.city_id_request import search_city
from database.chat_users_db import create_db, set_info
from handlers.default_heandlers.start_help import cancel_request
from keyboards.inline.keyboard_inline import city_choice_keyboard
from loader import bot
from states.user_states import UserState


@logger.catch
@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def get_city(message: types.Message) -> None:
    """
    Функция, которая реагирует на команды /lowprice, /highprice, /bestdeal.
    Принимает от пользователя название города, в котором требуется осуществить поиск.
    :param message: сообщение пользователя с одной из команд /lowprice, /highprice, /bestdeal.
    :return: None
    """
    logger.info(f'User {message.chat.id} used command {message.text}')
    chat_id = message.chat.id
    create_db(user_id=chat_id)
    set_info(column='command', value=message.text[1:], user_id=chat_id)
    set_info(column='request_time', value=datetime.today().strftime("%X %x"), user_id=chat_id)
    set_info(column='checkIn', value=None, user_id=message.chat.id)
    set_info(column='checkOut', value=None, user_id=message.chat.id)
    msg = bot.send_message(chat_id=message.chat.id, text='Укажите в каком городе ищем отель (города РФ временно не '
                                                         'доступны):')
    bot.set_state(message.from_user.id, UserState.command, message.chat.id)
    bot.register_next_step_handler(message=msg, callback=choice_city)


@logger.catch
def choice_city(message: types.Message) -> None:
    """
    Функция уточнения населенного пункта. Вызывает функцию city_choice_keyboard и выводит клавиатуру с вариантами
    найденными на rapidapi. Сохраняет информацию о введенном населенном пункте пользователем в виде строки
    в словарь c ключом 'name_city'
    :param message: сообщение пользователя с одной из команд /lowprice, /highprice, /bestdeal.
    :return: None
    """

    if message.text == '/help':
        cancel_request(message)
        return
    bot.send_message(chat_id=message.chat.id, text='Ведется поиск...')
    chat_id = message.chat.id
    city = message.text.title()
    city_list = search_city(city=city)
    if city_list is None:
        bot.send_message(chat_id=message.chat.id, text='Не удается получить информацию с сайта.'
                                                       'Повторите запрос позднее.')
        return
    if len(city_list) == 0:
        logger.info(f'City for user {message.chat.id} is not found')
        msg = bot.send_message(chat_id=chat_id, text=f'Город {city} не найден. Повторите ввод.')
        bot.register_next_step_handler(message=msg, callback=choice_city)
    else:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id + 1)
        new_markup = city_choice_keyboard(city_list)
        if new_markup is not None:
            msg = bot.send_message(message.from_user.id, 'Уточните место:',
                                   reply_markup=new_markup)
            bot.set_state(message.from_user.id, UserState.command, message.chat.id)
            bot.register_next_step_handler(message=msg, callback=city_choice_keyboard)
