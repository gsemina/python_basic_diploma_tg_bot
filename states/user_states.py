from telebot.handler_backends import State, StatesGroup


class UserInputState(StatesGroup):
    """Класс состояния пользователя"""
    command = State()  # команда, которую выбрал пользователь
    input_city = State()  # город, который ввел пользователь
    destinationId = State()  # запись id города
    quantity_hotels = State()  # количество отелей, нужное пользователю
    photo_count = State()  # количество фотографий
    input_date = State()  # ввод даты (заезда, выезда)
    priceMin = State()  # минимальная стоимость отеля
    priceMax = State()  # максимальная стоимость отеля
    start_distance_to_center = State()  # начало диапазона расстояния от центра
    end_distance_to_center = State()  # конец диапазона расстояния от центра
    history_select = State()  # выбор истории поиска


class UserInputInfo:
    pass