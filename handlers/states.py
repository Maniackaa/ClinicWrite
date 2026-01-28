"""
FSM состояния для записи на прием
"""
from aiogram.fsm.state import State, StatesGroup


class AppointmentStates(StatesGroup):
    """Состояния для процесса записи на прием"""
    waiting_for_name = State()  # Ожидание ввода имени
    waiting_for_phone = State()  # Ожидание ввода телефона
