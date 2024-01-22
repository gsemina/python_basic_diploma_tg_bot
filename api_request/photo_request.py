import requests
import re
import json
from loguru import logger

from api_request.city_id_request import request_api
from config_data.config import headers
from utils.different import make_photo_url


@logger.catch
def get_photo(hotel_id: str, photos_count=5) -> list | None:
    """Функция формирования и обработки запроса для получения ссылок на фотографии отеля. Словарь с информацией
    о фотографиях обрабатывается с помощью функции make_photo_url. Возвращает список со ссылками на фото в количестве
    :param photos_count: количество фотографий отеля.
    :param hotel_id: id отеля, для запроса.
    :return: список словарей из найденных фотографий в формате "Фотография": "ссылка на фотографию отеля".
    """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel_id}

    photo_response = request_api(url=url,  headers=headers, querystring=querystring)
    pattern = r'(?<=,)"hotelImages":.+?(?=,"roomImages)'
    find_photo = re.search(pattern, photo_response)
    try:
        if find_photo:
            results = json.loads(f"{{{find_photo[0]}}}")
            url_list = make_photo_url(photos_count=photos_count, photo_data=results)
            return url_list
        else:
            return None
    except requests.exceptions.RequestException as e:
        logger.info(f'{e} exceptions on step "get_photo"')
        return None
