# -*- coding: utf8 -*-

from datetime import date

import datetime
from loguru import logger
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar

from database.chat_users_db import get_info, set_info
from keyboards.inline.keyboard_inline import yes_or_no
from loader import bot


@logger.catch
def get_check_in_out_date(message: types.Message) -> None:
    """
    Функция, которая вызывает календарь для выбора даты заезда в отель.
    :param message: сообщение с выбором дат.
    :return: None
    """
    calendar, step = DetailedTelegramCalendar(locale='ru', min_date=date.today()).build()
    bot.send_message(chat_id=message.chat.id,
                     text=f"Год",
                     reply_markup=calendar)


@logger.catch
@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(call: types.CallbackQuery) -> None:
    """
    Функция. Принимает и обрабатывает данные календаря. Вносит даты заезда и выезда из отеля в бд.
    :param call: ответ на выбранные даты.
    :return: None
    """
    choice, key, step = DetailedTelegramCalendar(locale='ru', min_date=date.today()).process(call.data)
    if not choice and key:
        LSTEP = {"m": "Месяц", "d": "День"}
        bot.edit_message_text(f"{LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif choice:
        bot.delete_message(chat_id=int(call.message.chat.id), message_id=call.message.message_id)
        if get_info(call.message.chat.id)[11] is None:
            bot.send_message(chat_id=call.message.chat.id, text=f"Вы выбрали {choice}")
            set_info(column='checkIn', value=str(choice), user_id=call.message.chat.id)
            logger.info(f'User select {call.from_user.id} as IN date.')
            bot.send_message(chat_id=call.message.chat.id, text='Выберите дату выезда.')
            get_check_in_out_date(call.message)
        elif get_info(call.message.chat.id)[12] is None:
            bot.send_message(chat_id=call.message.chat.id, text=f"Вы выбрали {choice}")
            set_info(column='checkOut', value=str(choice), user_id=call.message.chat.id)
            logger.info(f'User select {call.from_user.id} as OUT date.')
            bot.send_message(chat_id=call.message.chat.id, text='Загрузить фото отеля?', reply_markup=yes_or_no())
        else:
            bot.send_message(chat_id=call.message.chat.id, text='Дата выезда не может совпадать или быть раньше '
                                                                'даты заезда.\nВыберите дату заезда.')
            set_info(column='checkIn', value=None, user_id=call.from_user.id)
            logger.info(f'User select wrong OUT date, IN date deleted.')
            get_check_in_out_date(call.message)


def calculate_days(in_date: str, out_date: str) -> int:
    """Считает количество дней из дат введенных пользователем
    """
    pattern = '%Y-%m-%d'
    day_1 = datetime.datetime.strptime(in_date, pattern)
    day_2 = datetime.datetime.strptime(out_date, pattern)
    result = day_2 - day_1
    number_days = result.days
    return number_days
