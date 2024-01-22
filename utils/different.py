# -*- coding: utf-8 -*-

from loguru import logger
from typing import Any


@logger.catch
def make_photo_url(photos_count: int, photo_data: dict) -> list[Any] | None:
    """Проходит по словарю и возвращает список из строк со ссылками на фотографии в количестве photos_count
    :param photos_count: количество фотографий.
    :param photo_data: словарь с информацией о фотографиях.
    :return: список из строк со ссылками на фотографии.
    """
    photos_url = []
    for number in range(photos_count):
        try:
            new_photo = photo_data['hotelImages'][number]['baseUrl']
            new_photo_url = new_photo.format(size=photo_data['hotelImages'][number]['sizes'][0]['suffix'])
        except KeyError:
            return None
        photos_url.append(new_photo_url)
    return photos_url


@logger.catch
def string_to_float(string: str) -> float:
    """
    Функция. Преобразует текстовое значение числа в вещественное значение.
    :param string: строка, содержащая текстовое значение вещественного числа.
    :return: вещественное значение числа
    """
    string_elements = string.split()
    number_elem = string_elements[0].split(',')
    if len(number_elem) != 1:
        float_number = float('.'.join(number_elem))
    else:
        float_number = float(number_elem[0])
    return float_number
