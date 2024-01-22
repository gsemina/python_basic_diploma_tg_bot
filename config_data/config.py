import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

headers = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': os.getenv('RAPID_API_KEY')
}
URL_HOST = 'https://hotels4.p.rapidapi.com/'
URL_PATHS = {
    'locations': 'locations/v2/search',
    'properties': 'properties/list',
    'photos': 'properties/get-hotel-photos'
}

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
DEFAULT_COMMANDS = (
    ('start', 'Запустить бота'),
    ('help', 'Вывести справку'),
    ('survey', 'Опрос'),
    ('lowprice', "Вывод самых дешёвых отелей в городе"),
    ('highprice', "Вывод самых дорогих отелей в городе"),
    ('bestdeal', "вывод отелей, наиболее подходящих по цене и расположению от центра"),
    ('history', "Вывод истории поиска отелей")
)
