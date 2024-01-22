# -*- coding: utf8 -*-
from datetime import datetime
from typing import List
import json
import re

import requests
from loguru import logger

from api_request.city_id_request import request_api
from config_data.config import headers
from utils.different import string_to_float


@logger.catch
def hotels_info_for_bestdeal(town_id: str,
                             command: str,
                             count_of_hotels: int,
                             min_price: int,
                             max_price: int,
                             min_distance: int,
                             max_distance: int,
                             in_date: str,
                             out_date: str) -> List[dict] or None:
    """
    Функция. Осуществляет запрос к API Hotels для получения списка отелей
    и их характеристик по-заданному ID города для команд bestdeal.
    :param command: тип запроса, который выбрал пользователь.
    :param town_id: id города, для запроса.
    :param count_of_hotels: количество отелей, которое запросил пользователь.
    :param min_price: минимальная цена проживания.
    :param max_price: максимальная цена проживания.
    :param min_distance: минимальная удаленность отеля от центра города.
    :param max_distance: максимальная удаленность отеля от центра города.
    :param in_date: дата заезда в отель.
    :param out_date: дата выезда из отеля.
    :return: список словарей из найденных отелей и их характеристик в формате:
        "ID": "цифровое значение ID города"
        "Наименование": "полное наименование отеля"
        "Адрес": "полный адрес отеля"
        "Рейтинг": "цифровое значение рейтинга отеля"
        "Расстояние": "расстояние от центра города до отеля"
        "Цена": "стоимость пребывания в отеле за сутки"
        "Цена за все время": "стоимость пребывания в отеле за весь период"
    """

    url_hotels = 'https://hotels4.p.rapidapi.com/properties/list'
    querystring = {"destinationId": town_id,
                   "pageNumber": "1",
                   "checkIn": in_date,
                   "checkOut": out_date,
                   "adults1": "1",
                   "priceMin": min_price,
                   "priceMax": max_price,
                   "sortOrder": "PRICE",
                   "locale": "ru_RU",
                   "currency": "RUB",
                   }
    if command == 'highprice':
        querystring['sortOrder'] = 'PRICE_HIGHEST_FIRST'
    try:
        response = request_api(url=url_hotels, headers=headers, querystring=querystring)
        pattern = r'"results".+?(?=,"pagination")'
        find = re.search(pattern, str(response))
        find = json.loads(f"{{{find[0]}}}")
        hotels_list = [{'id': hotel['id'],
                        'name': hotel['name'],
                        'address': hotel.get('address', {}).get('streetAddress'),
                        'rating': str(hotel['starRating']) + '*',
                        'distance': hotel['landmarks'][0]['distance'],
                        'cur_price': hotel['ratePlan']['price']['current'],
                        'overall_price': str(int(
                            (datetime.strptime(out_date, "%Y-%m-%d").date() -
                             datetime.strptime(in_date, "%Y-%m-%d").date()).days) *
                                             int(hotel['ratePlan']['price']['exactCurrent'])) + ' RUB'
                        }
                       for hotel in find['results']]

        for dicts in hotels_list:
            for key, value in dicts.items():
                if value is None:
                    dicts[key] = 'Информация отсутствует'
        bestdeal_hotels_list = list(filter(lambda elem:
                                           max_distance >= string_to_float(elem['distance']) >= min_distance,
                                           hotels_list))

        return bestdeal_hotels_list[:count_of_hotels]
    except requests.exceptions.RequestException as e:
        logger.info(f'{e} exceptions on step "hotels_info_for_bestdeal"')
        return None
