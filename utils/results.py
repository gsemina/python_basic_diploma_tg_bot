#-*- coding: utf8 -*-
import telebot
from loguru import logger
from telebot import types

from api_request.hotel_id_request import hotels_info_for_bestdeal
from api_request.photo_request import get_photo
from database.chat_users_db import get_info

from handlers.custom_heandlers.history import create_history, set_history_info

from loader import bot


@logger.catch
def result(user_id) -> None:
    """
    Функция. Осуществляет вывод информации о найденных отелях и их фотографии.
    :param user_id: id пользователя, по чьему запросу будет осуществлен вывод данных.
    :return: None
    """
    bot.send_message(chat_id=user_id, text='Ведется поиск отелей по заданным параметрам...')
    info_from_bd = get_info(user_id=user_id)
    hotels_history_list = []

    if info_from_bd[1] == 'bestdeal':
        request_result = hotels_info_for_bestdeal(town_id=info_from_bd[2],
                                                  count_of_hotels=info_from_bd[4],
                                                  min_price=info_from_bd[6],
                                                  max_price=info_from_bd[7],
                                                  min_distance=info_from_bd[8],
                                                  max_distance=info_from_bd[9],
                                                  command=info_from_bd[1],
                                                  in_date=info_from_bd[11],
                                                  out_date=info_from_bd[12]
                                                  )
    else:
        request_result = hotels_info_for_bestdeal(town_id=info_from_bd[2],
                                                  count_of_hotels=info_from_bd[4],
                                                  min_price=0,
                                                  max_price=9999999,
                                                  min_distance=0,
                                                  max_distance=999,
                                                  command=info_from_bd[1],
                                                  in_date=info_from_bd[11],
                                                  out_date=info_from_bd[12])

    if request_result is None:
        bot.send_message(chat_id=user_id, text='Не удается получить информацию с сайта.'
                                               'Повторите запрос позднее.')
        return
    elif len(request_result) == 0:
        bot.send_message(chat_id=user_id, text='Отели по заданным условиям не найдены.')
        return

    for data in request_result:
        request_answer = f'{"*" * 56}\n' \
                         f'Название отеля: {data.get("name")}\n' \
                         f'Адрес: {data.get("address")}\n' \
                         f'Рейтинг: {data.get("rating")}\n' \
                         f'Расстояние от центра города: {data.get("distance")}\n' \
                         f'Цена за ночь: {data.get("cur_price")}\n' \
                         f'Цена за все время: {data.get("overall_price")}\n' \
                         f'Сcылка на отель: https://hotels.com/ho{data.get("id")}'
        hotels_history_list.append(f'{data.get("name")}')
        bot.send_message(chat_id=user_id, text=request_answer, disable_web_page_preview=True)
        if info_from_bd[5] != 0:
            photos_list = []
            photos = get_photo(hotel_id=data['id'])

            if request_result is None:
                bot.send_message(chat_id=user_id, text='Не удается получить информацию с сайта.'
                                                       'Повторите запрос позднее.')
                return

            for elem in photos[:info_from_bd[5]]:
                if elem is not None:
                    photos_list.append(types.InputMediaPhoto(elem.replace('{size}', 'z')))
            try:
                bot.send_media_group(chat_id=user_id, media=photos_list)
            except telebot.apihelper.ApiTelegramException:
                bot.send_message(chat_id=user_id, text='По данному отелю не удалось получить фотографии.')

    create_history(req_time=info_from_bd[10], user_id=user_id)
    set_history_info(command_type=str(info_from_bd[1]),
                     request_result=str(hotels_history_list),
                     user_id=user_id)
    bot.send_message(chat_id=user_id, text='Поиск завершен.')
