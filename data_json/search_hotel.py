import json
from telebot.types import Dict


def search_hotels(response_text: str, command: str,
                  start_distance_to_center: str,
                  end_distance_to_center: str) -> Dict:
    """
    Принимает ответ от сервера, выбранную команду сортировки, а так же пределы диапазона
    расстояния от центра города. Возвращает отсортированный словарь.
    : param response_text : str Ответ от сервера, в котором содержится информация об отелях.
    : param command : str Команда сортировки.
    : param start_distance_to_center : str Начало диапазона растояния до центра.
    : param end_distance_to_center : str Конец диапазона растояния до центра.
    : return hotels_data : Dict Возвращает словарь с данными об отелях
    """
    data = json.loads(response_text)
    if not data:
        raise LookupError('Запрос пуст...')
    if 'errors' in data.keys():
        return {'error': data['errors'][0]['message']}  #исключаем ошибку при поиске в некоторых городах

    hotels_data = {}
    for hotel in data['data']['propertySearch']['properties']:
        try:
            hotels_data[hotel['id']] = {
                'name': hotel['name'], 'id': hotel['id'],
                'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
                'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
                'price': hotel['price']['lead']['amount']
            }
        except (KeyError, TypeError):
            continue
    # Сортируем по цене, от высокой стоимости, к меньшей.
    if command == '/highprice':
        hotels_data = {
            key: value for key, value in
            sorted(hotels_data.items(), key=lambda hotel_id: hotel_id[1]['price'], reverse=True)
        }
    # Обнуляем созданный ранее словарь и добавляем туда только те отели, которые соответствуют диапазону.
    elif command == '/bestdeal':
        hotels_data = {}
        for hotel in data['data']['propertySearch']["properties"]:
            if float(start_distance_to_center) \
                    < hotel['destinationInfo']['distanceFromDestination']['value'] \
                    < float(end_distance_to_center):
                hotels_data[hotel['id']] = {
                    'name': hotel['name'], 'id': hotel['id'],
                    'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
                    'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
                    'price': hotel['price']['lead']['amount']
                }

    return hotels_data
