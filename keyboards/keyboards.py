from aiogram.types import KeyboardButton, ReplyKeyboardMarkup,\
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder



kb1 = {
    # 'Мои заказы': 'my_orders',
    'Удалить заказ': 'delete_order',
}


def custom_kb(width: int, buttons_dict: dict) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = []
    for key, val in buttons_dict.items():
        callback_button = InlineKeyboardButton(
            text=key,
            callback_data=val)
        buttons.append(callback_button)
    kb_builder.row(*buttons, width=width)
    return kb_builder.as_markup()


start_kb = custom_kb(2, kb1)


yes_no_kb_btn = {
    'Отменить': 'cancel',
    'Подтвердить': 'confirm',
}

yes_no_kb = custom_kb(2, yes_no_kb_btn)


# Главное меню для клиники
def get_main_menu_kb() -> InlineKeyboardMarkup:
    """Создает клавиатуру главного меню"""
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(text="🔵 Прайс", callback_data="menu_price")
    )
    kb_builder.row(
        InlineKeyboardButton(text="🔵 Перейти в ТГ-канал клиники", url="https://t.me/royalclinicmos")
    )
    kb_builder.row(
        InlineKeyboardButton(text="🔵 Контакты", callback_data="menu_contacts")
    )
    kb_builder.row(
        InlineKeyboardButton(text="🔵 Записаться на прием", callback_data="menu_appointment")
    )
    return kb_builder.as_markup()


def get_price_kb() -> InlineKeyboardMarkup:
    """Создает клавиатуру для раздела Прайс"""
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(text="📥 Скачать прайс", callback_data="download_price")
    )
    kb_builder.row(
        InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")
    )
    return kb_builder.as_markup()


def get_contacts_kb() -> InlineKeyboardMarkup:
    """Создает клавиатуру для раздела Контакты"""
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")
    )
    return kb_builder.as_markup()


def get_appointment_kb() -> InlineKeyboardMarkup:
    """Создает клавиатуру для раздела Записаться на прием"""
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")
    )
    return kb_builder.as_markup()


def get_professions_kb() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора профессии врача"""
    from data.doctors_data import PROFESSION_NAMES
    
    kb_builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки для каждой профессии
    for profession_key, profession_name in PROFESSION_NAMES.items():
        kb_builder.row(
            InlineKeyboardButton(
                text=profession_name,
                callback_data=f"profession_{profession_key}"
            )
        )
    
    kb_builder.row(
        InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")
    )
    return kb_builder.as_markup()


def get_doctors_kb(profession: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора врача по профессии"""
    from data.doctors_data import PROFESSIONS, DOCTOR_IDS
    
    kb_builder = InlineKeyboardBuilder()
    
    # Получаем список врачей для данной профессии
    doctors = PROFESSIONS.get(profession, [])
    
    # Добавляем кнопки для каждого врача (используем короткие ID)
    for doctor_name in doctors:
        doctor_id = DOCTOR_IDS.get(doctor_name, doctor_name.replace(' ', '_')[:20])
        # Формат: doc_<doctor_id>_<profession> (максимум 64 байта)
        callback_data = f"doc_{doctor_id}_{profession[:10]}"
        kb_builder.row(
            InlineKeyboardButton(
                text=f"• {doctor_name}",
                callback_data=callback_data
            )
        )
    
    kb_builder.row(
        InlineKeyboardButton(text="⬅️ Назад к выбору услуги", callback_data="menu_appointment")
    )
    return kb_builder.as_markup()


def get_doctor_info_kb(doctor_name: str, profession: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру для информации о враче"""
    from data.doctors_data import DOCTOR_IDS
    
    kb_builder = InlineKeyboardBuilder()
    
    # Используем короткий ID для callback_data
    doctor_id = DOCTOR_IDS.get(doctor_name, doctor_name.replace(' ', '_')[:20])
    
    kb_builder.row(
        InlineKeyboardButton(
            text="📝 Записаться на прием",
            callback_data=f"appoint_{doctor_id}"
        )
    )
    kb_builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад к списку врачей",
            callback_data=f"back_docs_{profession[:10]}"
        )
    )
    return kb_builder.as_markup()


def get_cancel_kb() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопкой отмены"""
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_appointment")
    )
    return kb_builder.as_markup()


def get_phone_kb() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопкой поделиться телефоном"""
    kb_builder = ReplyKeyboardBuilder()
    kb_builder.row(
        KeyboardButton(text="📱 Поделиться телефоном", request_contact=True)
    )
    kb_builder.row(
        KeyboardButton(text="❌ Отменить")
    )
    return kb_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
