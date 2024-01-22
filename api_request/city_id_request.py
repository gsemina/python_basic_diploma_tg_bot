import requests
import re
import json
from loguru import logger
from typing import Optional, List

from config_data.config import headers


@logger.catch
def request_api(url: str, headers: dict, querystring: dict) -> str | None:
    """
    Универсальная функция по отправке запроса на rapidapi.
    :param url: url
    :param headers: rapid_api_host, key
    :param querystring: словарь с ключами поиска
    """
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=30)
        if response.status_code == requests.codes.ok:
            logger.info('Request to RAPID API')
            return response.text
        elif response.status_code == 429:
            raise requests.exceptions.ConnectionError(f'{response.status_code} - Закончился лимит запросов к API')
        else:
            raise ConnectionError(f'Ошибка {response.status_code} при запросе к API')
    except requests.ConnectionError as e:
        logger.info(f'{e} exceptions Connection Error. Make sure you are connected to Internet.')
    except requests.Timeout as e:
        logger.info(f'{e} exceptions "ConnectTimeout"')
    except ConnectionResetError as conn:
        logger.error(conn)
    except ConnectionError as conn:
        logger.error(conn)
    except Exception as api_ex:
        logger.error(f'Having problems with the site - {api_ex}')


@logger.catch
def search_city(city: Optional[str]) -> List[dict] or None:
    """
    Функция. Осуществляет запрос к API Hotels для получения списка городов,
    подходящих под заданное название.
    :param city: название города для запроса, которое указал пользователь.
    :return: список словарей из найденных городов в формате "ID города": "полное наименование города".
    """

    url_location = 'https://hotels4.p.rapidapi.com/locations/search'
    querystring = {'query': city, 'locale': "ru_RU"}
    response = request_api(url=url_location, headers=headers, querystring=querystring)
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, str(response))
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        city_list = list()
        try:
            for city_info in suggestions['entities']:
                result_destination = re.sub(r'<.*>\S*', '', city_info['caption'])
                if result_destination.find(city_info['name']) == -1:
                    result_destination = ''.join([city_info['name'], ',', result_destination])
                city_list.append({'city_name': result_destination, 'destination_id': city_info['destinationId']})
            logger.info(f'Make a list of cities for user')
            return city_list
        except requests.exceptions.RequestException as e:
            logger.info(f'{e} exceptions on step "search_city"')
            return None
