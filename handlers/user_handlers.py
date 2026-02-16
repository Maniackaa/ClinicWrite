import re
import datetime
from typing import Any

import pytz
import structlog
from aiogram import Router, Bot, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile, InputFile, Contact, ReplyKeyboardRemove

from config_data.conf import conf, BASE_DIR
from main import send_telegram_message
from handlers.states import AppointmentStates
from keyboards.keyboards import (
    get_main_menu_kb,
    get_price_kb,
    get_contacts_kb,
    get_appointment_kb,
    get_professions_kb,
    get_doctors_kb,
    get_doctor_info_kb,
    get_cancel_kb,
    get_phone_kb
)
from data.doctors_data import (
    DOCTORS,
    PROFESSION_NAMES,
    DOCTOR_IDS,
    DOCTOR_IDS_REVERSE,
    PROFESSION_KEY_MAP,
    get_photo_id,
    save_photo_id,
)

logger = structlog.get_logger(__name__)
router = Router()

CURRENCY_REGEX = re.compile(
    r'(💸|💵)1\s*➡️\s*₫\s*([\d\s]+)',
    re.MULTILINE
)


@router.channel_post()
async def channel_post_handler(message: Message, bot, scheduler) -> Any:
    try:
        logger.info(f'Прочитал сообщение в канале {message.chat.id}')
        numbers = re.findall(r'➡️\s*₫\s*([\d\s]+)', message.text)
        # Убираем пробелы в числах, потом форматируем обратно с пробелами между разрядами
        formatted = [f"{int(n.replace(' ', '')):,}".replace(",", " ") for n in numbers[:3]]
        logger.info(formatted)
        if formatted:
            new_text = f"""<b>Друзья </b><tg-emoji emoji-id="5442678635909621223">❤️</tg-emoji><b>
    к</b>оманда группы 
    <i>Кто летит?📦Вьетнам!</i>
     рада представить вам сервис <a href="https://t.me/KREXPEXexchange"><i>ОБМЕНА ВАЛЮТЫ</i></a><b>
     </b><tg-emoji emoji-id="5472030678633684592">💸</tg-emoji><b> </b><i>в городе Нячанг</i>

    <b><i>ВАШ ЛУЧШИЙ КУРС </i></b>

    <tg-emoji emoji-id="5265122991380897957">💸</tg-emoji><b>1       </b><tg-emoji emoji-id="5379894627883032944">➡️</tg-emoji>   <b>₫ {formatted[0]}
    </b><tg-emoji emoji-id="5409048419211682843">💵</tg-emoji><b>1       </b><tg-emoji emoji-id="5379894627883032944">➡️</tg-emoji><b>  </b> <b>₫</b> <b>{formatted[1]}
    </b><tg-emoji emoji-id="5264945652181247629">💸</tg-emoji><b>1       </b><tg-emoji emoji-id="5379894627883032944">➡️</tg-emoji>   <b>₫</b> <b>{formatted[2]}

    </b><tg-emoji emoji-id="5217497254381754877">✅</tg-emoji> <i>от ₽20 000 - бесплатная доставка</i>
    <tg-emoji emoji-id="5217497254381754877">✅</tg-emoji> <i>от ₽100 000 - курс еще приятней</i>
    <tg-emoji emoji-id="5217497254381754877">✅</tg-emoji> <i>все сделки при личной встрече</i>
    <tg-emoji emoji-id="5217497254381754877">✅</tg-emoji> <i>другие уникальные услуги</i>

    <a href="https://t.me/KREXPEXexchange"><i>https://t.me/KREXPEXexchange</i></a>

    <tg-emoji emoji-id="5442678635909621223">❤️</tg-emoji>Мы дорожим нашим комьюнити, по этой причине делаем все, чтобы вы получали первоклассный сервис!"""
            new_text = f"""Друзья ❤️
    команда группы 
    <i>Кто летит?📦Вьетнам!</i>
    рада представить вам сервис    ОБМЕНА ВАЛЮТЫ (https://t.me/KREXPEXexchange) 💸
    в городе Нячанг

    <b><i>ВАШ ЛУЧШИЙ КУРС </i></b>

    1 <code>rub   </code>➡️   ₫ {formatted[0]}
    1 <code>usd   </code>➡️   ₫ {formatted[1]}
    1 <code>usdt  </code>➡️   ₫ {formatted[2]}

    ✅ от ₽20 000 - бесплатная доставка
    ✅ от ₽100 000 - курс еще приятней
    ✅ все сделки при личной встрече
    ✅ другие уникальные услуги

    https://t.me/KREXPEXexchange

    ❤️Мы дорожим нашим комьюнити, по этой причине делаем все, чтобы вы получали первоклассный сервис!"""
            moscow = pytz.timezone("Asia/Krasnoyarsk")
            now = datetime.datetime.now(moscow)
            send_at = now.replace(hour=12, minute=0, second=0, microsecond=0)
            logger.info(f'now: {now} send_at: {send_at}')
            # send_at = now + datetime.timedelta(seconds=1)
            scheduler.add_job(
                send_telegram_message,
                "date",
                run_date=send_at,
                args=[conf.tg_bot.GROUP_ID, new_text],
                id=f"send_{message.chat.id}_{send_at.timestamp()}"
            )
            logger.info(len(new_text))
    except Exception as e:
        logger.error(e, exc_info=True)

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    """Обработчик команды /start с приветственным сообщением"""
    try:
        logger.info(f'cmd_start: пользователь {message.from_user.id} ({message.from_user.username}) {message.chat.id}')
        welcome_text = """Здравствуй, королевский друг ROYAL Clinic. 
Приглашаем вас в волшебный научный мир счастливого родительства!"""
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_kb(),
            parse_mode=ParseMode.HTML
        )
        logger.info(f'Приветственное сообщение отправлено пользователю {message.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в cmd_start: {e}', exc_info=True)


# Обработчик кнопки "Назад в меню"
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, bot: Bot):
    """Обработчик кнопки Назад в меню"""
    try:
        logger.info(f'back_to_menu: пользователь {callback.from_user.id}')
        welcome_text = """Здравствуй, королевский друг ROYAL Clinic. 
Приглашаем вас в волшебный научный мир счастливого родительства!"""
        
        # Если сообщение содержит фото, отправляем новое сообщение вместо редактирования
        if callback.message.photo:
            try:
                await callback.message.delete()
            except Exception as delete_error:
                logger.warning(f'Не удалось удалить сообщение с фото: {delete_error}')
            
            await callback.message.answer(
                welcome_text,
                reply_markup=get_main_menu_kb(),
                parse_mode=ParseMode.HTML
            )
        else:
            try:
                await callback.message.edit_text(
                    welcome_text,
                    reply_markup=get_main_menu_kb(),
                    parse_mode=ParseMode.HTML
                )
            except Exception as edit_error:
                # Если не удалось отредактировать, отправляем новое сообщение
                logger.warning(f'Не удалось отредактировать сообщение, отправляем новое: {edit_error}')
                await callback.message.answer(
                    welcome_text,
                    reply_markup=get_main_menu_kb(),
                    parse_mode=ParseMode.HTML
                )
        
        await callback.answer()
        logger.info(f'Главное меню показано пользователю {callback.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в back_to_menu: {e}', exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except:
            pass


# Обработчик кнопки "Прайс"
@router.callback_query(F.data == "menu_price")
async def menu_price(callback: CallbackQuery, bot: Bot):
    """Обработчик кнопки Прайс"""
    try:
        logger.info(f'menu_price: пользователь {callback.from_user.id}')
        text = "🟧 Прайс\n\nВыберите действие:"
        await callback.message.edit_text(
            text,
            reply_markup=get_price_kb(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        logger.info(f'Меню прайса показано пользователю {callback.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в menu_price: {e}', exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except:
            pass


# Обработчик команды для получения file_id прайса (только для админов)
@router.message(Command("get_price_file_id"))
async def get_price_file_id(message: Message, bot: Bot):
    """Обработчик команды для отправки файла прайса и получения его file_id"""
    try:
        logger.info(f'get_price_file_id: пользователь {message.from_user.id} ({message.from_user.username})')
        # Проверяем, что пользователь - админ
        if str(message.from_user.id) not in conf.tg_bot.admin_ids:
            logger.warning(f'Попытка доступа к админ-команде от неавторизованного пользователя {message.from_user.id}')
            await message.answer("❌ У вас нет прав для выполнения этой команды.")
            return
        
        data_dir = BASE_DIR / 'data'
        
        # Пробуем найти файл прайса
        possible_names = [
            'Royal Clinic Прайс-лист.pdf',
            'Royal Clinic Прайс-лист.pdf',
            'price.pdf',
        ]
        
        price_file_path = None
        for name in possible_names:
            path = data_dir / name
            if path.exists():
                price_file_path = path
                break
        
        # Если не нашли по точному имени, ищем любой PDF файл в папке data
        if not price_file_path:
            pdf_files = list(data_dir.glob('*.pdf'))
            if pdf_files:
                price_file_path = pdf_files[0]
        
        if price_file_path and price_file_path.exists():
            try:
                logger.info(f'Отправка файла прайса для получения file_id: {price_file_path}')
                price_file = FSInputFile(price_file_path)
                
                # Отправляем файл
                sent_message = await bot.send_document(
                    chat_id=message.chat.id,
                    document=price_file,
                    caption="📥 Прайс ROYAL Clinic"
                )
                
                # Получаем file_id из отправленного документа
                file_id = sent_message.document.file_id
                
                logger.info("=" * 80)
                logger.info(f"FILE_ID ПРАЙСА: {file_id}")
                logger.info("=" * 80)
                logger.info(f"Добавьте в .env файл: PRICE_FILE_ID={file_id}")
                logger.info("=" * 80)
                
                await message.answer(
                    f"✅ Файл отправлен!\n\n"
                    f"📋 <b>FILE_ID:</b> <code>{file_id}</code>\n\n"
                    f"Добавьте в .env файл:\n"
                    f"<code>PRICE_FILE_ID={file_id}</code>",
                    parse_mode=ParseMode.HTML
                )
                
            except Exception as send_error:
                logger.error(f'Ошибка при отправке файла прайса: {send_error}', exc_info=True)
                await message.answer(f"❌ Ошибка при отправке файла: {str(send_error)}")
        else:
            await message.answer("❌ Файл прайса не найден в папке data")
            logger.error(f'Файл прайса не найден в директории: {data_dir}')
            
    except Exception as e:
        logger.error(f'Ошибка в обработчике get_price_file_id: {e}', exc_info=True)
        await message.answer(f"❌ Произошла ошибка: {str(e)}")


@router.message(Command("get_video_id"))
async def cmd_get_video_id(message: Message):
    """Команда для админа: подсказка как получить file_id видео."""
    if str(message.from_user.id) not in conf.tg_bot.admin_ids:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    await message.answer(
        "📹 Отправьте видео следующим сообщением — в ответ пришлю <b>file_id</b>.\n\n"
        "Этот ID впишите в <code>data/doctors_data.py</code> в поле <code>video_id</code> у нужного врача. "
        "Тогда бот будет отправлять видео по ID без загрузки файла.",
        parse_mode=ParseMode.HTML
    )


@router.message(F.video)
async def admin_reply_video_id(message: Message):
    """Если админ отправил видео — отвечаем ему file_id для вставки в doctors_data."""
    if str(message.from_user.id) not in conf.tg_bot.admin_ids:
        return
    file_id = message.video.file_id
    logger.info(f"Админ {message.from_user.id} запросил file_id видео: {file_id[:40]}...")
    await message.answer(
        f"📋 <b>file_id видео:</b>\n<code>{file_id}</code>\n\n"
        f"Впишите в <code>data/doctors_data.py</code> в поле <code>video_id</code> для нужного врача.",
        parse_mode=ParseMode.HTML
    )


# Обработчик кнопки "Скачать прайс"
@router.callback_query(F.data == "download_price")
async def download_price(callback: CallbackQuery, bot: Bot):
    """Обработчик кнопки Скачать прайс - использует file_id если доступен"""
    try:
        logger.info(f'download_price: пользователь {callback.from_user.id}')
        await callback.answer("Загрузка прайса...")
        
        # Если есть file_id в конфиге, используем его (быстрее для больших файлов)
        if conf.tg_bot.price_file_id:
            try:
                logger.info(f'Отправка прайса по file_id пользователю {callback.from_user.id}')
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document=conf.tg_bot.price_file_id,
                    caption="📥 Прайс ROYAL Clinic"
                )
                logger.info('Прайс успешно отправлен по file_id')
                return
            except Exception as file_id_error:
                logger.warning(f'Ошибка при отправке по file_id, пробуем загрузить файл: {file_id_error}')
                # Продолжаем загрузку файла, если file_id не сработал
        
        # Если file_id нет или не сработал, загружаем файл
        data_dir = BASE_DIR / 'data'
        
        # Пробуем найти файл прайса
        possible_names = [
            'Royal Clinic Прайс-лист.pdf',
            'Royal Clinic Прайс-лист.pdf',
            'price.pdf',
        ]
        
        price_file_path = None
        for name in possible_names:
            path = data_dir / name
            if path.exists():
                price_file_path = path
                logger.info(f'Найден файл прайса по имени: {price_file_path}')
                break
        
        # Если не нашли по точному имени, ищем любой PDF файл в папке data
        if not price_file_path:
            pdf_files = list(data_dir.glob('*.pdf'))
            if pdf_files:
                price_file_path = pdf_files[0]
                logger.info(f'Найден файл прайса: {price_file_path}')
        
        if price_file_path and price_file_path.exists():
            try:
                logger.info(f'Отправка файла прайса пользователю {callback.from_user.id}: {price_file_path}')
                price_file = FSInputFile(price_file_path)
                
                # Отправляем файл
                sent_message = await bot.send_document(
                    chat_id=callback.from_user.id,
                    document=price_file,
                    caption="📥 Прайс ROYAL Clinic"
                )
                logger.info(f'Файл прайса успешно отправлен. Message ID: {sent_message.message_id}')
                
            except Exception as send_error:
                logger.error(f'Ошибка при отправке файла прайса: {send_error}', exc_info=True)
                await callback.message.answer(
                    f"❌ Произошла ошибка при отправке файла: {str(send_error)}\n\nПожалуйста, попробуйте позже или свяжитесь с администратором.",
                    reply_markup=get_price_kb()
                )
        else:
            await callback.message.answer(
                "❌ Файл прайса не найден. Обратитесь к администратору.",
                reply_markup=get_price_kb()
            )
            await callback.answer("Файл не найден", show_alert=True)
            logger.error(f'Файл прайса не найден в директории: {data_dir}')
    except Exception as e:
        logger.error(f'Критическая ошибка в обработчике download_price: {e}', exc_info=True)
        try:
            await callback.answer("Произошла ошибка при отправке файла", show_alert=True)
        except:
            pass


# Обработчик кнопки "Контакты"
@router.callback_query(F.data == "menu_contacts")
async def menu_contacts(callback: CallbackQuery, bot: Bot):
    """Обработчик кнопки Контакты"""
    try:
        logger.info(f'menu_contacts: пользователь {callback.from_user.id}')
        contacts_text = """🟧 Контакты

📞 Номера телефонов:
<a href="tel:+79057777095">+7(905)-777-70-95</a>
<a href="tel:+79260440040">+7(926)-044-00-40</a>

🌐 Сайт клиники: <a href="https://royalclinicmoscow.ru">https://royalclinicmoscow.ru</a>

📍 Адрес: г. Москва, Севастопольский проспект 13А
🚇 м. Крымская, МЦК Крымская
🅿️ Собственная парковка"""
        
        # Проверяем наличие фото для контактов
        contact_photo_path = BASE_DIR / 'data' / 'photo' / 'contact.jpeg'
        logger.info(f'Проверка файла контактов: {contact_photo_path}, существует: {contact_photo_path.exists()}')
        
        if contact_photo_path.exists():
            # Если фото есть, отправляем его с текстом
            try:
                photo = FSInputFile(contact_photo_path)
                logger.info(f'Отправка фото контактов: {contact_photo_path}')
                # Отправляем фото с текстом
                await bot.send_photo(
                    chat_id=callback.from_user.id,
                    photo=photo,
                    caption=contacts_text,
                    reply_markup=get_contacts_kb(),
                    parse_mode=ParseMode.HTML
                )
                # Удаляем старое сообщение
                try:
                    await callback.message.delete()
                except Exception as delete_error:
                    logger.warning(f'Не удалось удалить сообщение: {delete_error}')
                await callback.answer()
                logger.info(f'Контакты с фото показаны пользователю {callback.from_user.id}')
            except Exception as photo_error:
                logger.error(f'Ошибка при отправке фото контактов: {photo_error}', exc_info=True)
                # Если не удалось отправить фото, отправляем текст
                await callback.message.edit_text(
                    contacts_text,
                    reply_markup=get_contacts_kb(),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                await callback.answer()
        else:
            logger.warning(f'Файл контактов не найден: {contact_photo_path}')
            # Если фото нет, редактируем текстовое сообщение
            await callback.message.edit_text(
                contacts_text,
                reply_markup=get_contacts_kb(),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            await callback.answer()
            logger.info(f'Контакты без фото показаны пользователю {callback.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в menu_contacts: {e}', exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except:
            pass


# Обработчик кнопки "Записаться на прием"
@router.callback_query(F.data == "menu_appointment")
async def menu_appointment(callback: CallbackQuery, bot: Bot):
    """Обработчик кнопки Записаться на прием - показывает список профессий"""
    try:
        logger.info(f'menu_appointment: пользователь {callback.from_user.id}')
        text = "🟧 Записаться на прием\n\nВыберите услугу:"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_professions_kb(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        logger.info(f'Список профессий показан пользователю {callback.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в menu_appointment: {e}', exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except:
            pass


# Обработчик выбора профессии
@router.callback_query(F.data.startswith("profession_"))
async def select_profession(callback: CallbackQuery, bot: Bot):
    """Обработчик выбора профессии - показывает список врачей"""
    try:
        profession_key = callback.data.replace("profession_", "")
        profession_name = PROFESSION_NAMES.get(profession_key, profession_key)
        logger.info(f'select_profession: пользователь {callback.from_user.id}, профессия={profession_key}')
        
        text = f"{profession_name}\n\nВыберите врача:"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_doctors_kb(profession_key),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        logger.info(f'Список врачей профессии {profession_key} показан пользователю {callback.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в select_profession: {e}', exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except:
            pass


# Обработчик выбора врача
@router.callback_query(F.data.startswith("doc_"))
async def select_doctor(callback: CallbackQuery, bot: Bot):
    """Обработчик выбора врача - показывает информацию о враче"""
    try:
        logger.info(f'select_doctor: пользователь {callback.from_user.id}, callback_data={callback.data}')
        # Извлекаем ID врача и профессию из callback_data
        # Формат: doc_<doctor_id>_<profession>
        # Профессия всегда в конце, разделяем с конца
        callback_data_clean = callback.data.replace("doc_", "")
        
        # Находим последнее подчеркивание - после него профессия
        last_underscore = callback_data_clean.rfind("_")
        if last_underscore == -1:
            logger.error(f'Неверный формат callback_data: {callback.data}')
            await callback.answer("Ошибка в данных", show_alert=True)
            return
        
        doctor_id = callback_data_clean[:last_underscore]
        profession = callback_data_clean[last_underscore + 1:]
        
        logger.debug(f'Извлечено: doctor_id={doctor_id}, profession={profession}')
        
        # Получаем имя врача по ID (ID уже без префикса doc_)
        doctor_name = DOCTOR_IDS_REVERSE.get(doctor_id)
        
        if not doctor_name:
            logger.error(f'Врач не найден по ID: {doctor_id}')
            await callback.answer("Врач не найден", show_alert=True)
            return
        
        doctor = DOCTORS.get(doctor_name)
        
        if not doctor:
            logger.error(f'Врач не найден в словаре DOCTORS: {doctor_name}')
            await callback.answer("Врач не найден", show_alert=True)
            return
        
        logger.info(f'Показ информации о враче: {doctor.name}, пользователь: {callback.from_user.id}')
        
        # Формируем текст с информацией о враче
        text = f"👨‍⚕️ <b>{doctor.name}</b>\n\n"
        text += f"Специальность: {doctor.profession}\n\n"
        text += f"{doctor.description}"
        
        # Видео отправляем только по video_id (файл с диска не отправляем)
        video_id = getattr(doctor, 'video_id', None)
        has_video = bool(video_id)
        has_photo = doctor.photo_filename and (BASE_DIR / 'data' / 'photo' / doctor.photo_filename).exists()
        
        if has_video or has_photo:
            await callback.message.delete()
            if has_video:
                await bot.send_video(
                    chat_id=callback.from_user.id,
                    video=video_id
                )
                logger.info(f'Видео отправлено для врача {doctor.name}')
            # 2) Затем фото с текстом и кнопкой «Записаться» или только текст с кнопкой
            kb = get_doctor_info_kb(doctor.name, profession)
            if has_photo:
                photo_id = get_photo_id(doctor.name)
                if photo_id:
                    sent = await bot.send_photo(
                        chat_id=callback.from_user.id,
                        photo=photo_id,
                        caption=text,
                        reply_markup=kb,
                        parse_mode=ParseMode.HTML
                    )
                else:
                    photo = FSInputFile(BASE_DIR / 'data' / 'photo' / doctor.photo_filename)
                    sent = await bot.send_photo(
                        chat_id=callback.from_user.id,
                        photo=photo,
                        caption=text,
                        reply_markup=kb,
                        parse_mode=ParseMode.HTML
                    )
                    if sent.photo:
                        save_photo_id(doctor.name, sent.photo[-1].file_id)
                        logger.info(f'Соранён photo_id для врача {doctor.name}')
            else:
                await bot.send_message(
                    chat_id=callback.from_user.id,
                    text=text,
                    reply_markup=kb,
                    parse_mode=ParseMode.HTML
                )
            await callback.answer()
            return
        
        # Нет ни видео, ни фото — только текст
        await callback.message.edit_text(
            text,
            reply_markup=get_doctor_info_kb(doctor.name, profession),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        logger.info(f'Информация о враче {doctor.name} отправлена пользователю {callback.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в select_doctor: {e}', exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except:
            pass


# Обработчик кнопки "Назад к списку врачей"
@router.callback_query(F.data.startswith("back_docs_"))
async def back_to_doctors(callback: CallbackQuery, bot: Bot):
    """Обработчик возврата к списку врачей"""
    try:
        profession_key_short = callback.data.replace("back_docs_", "")
        # Преобразуем обрезанный ключ в полный ключ профессии
        profession_key = PROFESSION_KEY_MAP.get(profession_key_short, profession_key_short)
        profession_name = PROFESSION_NAMES.get(profession_key, profession_key)
        logger.info(f'back_to_doctors: пользователь {callback.from_user.id}, профессия={profession_key} (из {profession_key_short})')
        
        text = f"{profession_name}\n\nВыберите врача:"
        
        # Если сообщение содержит фото, удаляем его и отправляем новое сообщение
        if callback.message.photo:
            try:
                await callback.message.delete()
            except Exception as delete_error:
                logger.warning(f'Не удалось удалить сообщение с фото: {delete_error}')
            
            await callback.message.answer(
                text,
                reply_markup=get_doctors_kb(profession_key),
                parse_mode=ParseMode.HTML
            )
        else:
            try:
                await callback.message.edit_text(
                    text,
                    reply_markup=get_doctors_kb(profession_key),
                    parse_mode=ParseMode.HTML
                )
            except Exception as edit_error:
                # Если не удалось отредактировать (сообщение удалено), отправляем новое
                logger.warning(f'Не удалось отредактировать сообщение при возврате к списку врачей, отправляем новое: {edit_error}')
                await callback.message.answer(
                    text,
                    reply_markup=get_doctors_kb(profession_key),
                    parse_mode=ParseMode.HTML
                )
        
        await callback.answer()
        logger.info(f'Возврат к списку врачей профессии {profession_key} для пользователя {callback.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в back_to_doctors: {e}', exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except:
            pass


# Обработчик кнопки "Записаться на прием" у врача
@router.callback_query(F.data.startswith("appoint_"))
async def start_appointment(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Обработчик начала записи на прием - запрашивает имя"""
    try:
        logger.info(f'start_appointment: пользователь {callback.from_user.id}, callback_data={callback.data}')
        doctor_id = callback.data.replace("appoint_", "")
        
        # Получаем имя врача по ID (ID без префикса doc_)
        doctor_name = DOCTOR_IDS_REVERSE.get(doctor_id)
        
        if not doctor_name:
            logger.error(f'Врач не найден по ID: {doctor_id}')
            await callback.answer("Врач не найден", show_alert=True)
            return
        
        doctor = DOCTORS.get(doctor_name)
        
        if not doctor:
            logger.error(f'Врач не найден в словаре DOCTORS: {doctor_name}')
            await callback.answer("Врач не найден", show_alert=True)
            return
        
        logger.info(f'Начало записи к врачу: {doctor.name}, пользователь: {callback.from_user.id}')
        
        # Сохраняем данные о враче в состояние
        await state.update_data(doctor_name=doctor.name, doctor_profession=doctor.profession)
        await state.set_state(AppointmentStates.waiting_for_name)
        
        text = f"📝 Запись к врачу: <b>{doctor.name}</b>\n\n"
        text += "Пожалуйста, введите ваше имя:"
        
        # Если сообщение содержит фото, отправляем новое сообщение вместо редактирования
        if callback.message.photo:
            await callback.message.answer(
                text,
                reply_markup=get_cancel_kb(),
                parse_mode=ParseMode.HTML
            )
        else:
            try:
                await callback.message.edit_text(
                    text,
                    reply_markup=get_cancel_kb(),
                    parse_mode=ParseMode.HTML
                )
            except Exception as edit_error:
                # Если не удалось отредактировать, отправляем новое сообщение
                logger.warning(f'Не удалось отредактировать сообщение, отправляем новое: {edit_error}')
                await callback.message.answer(
                    text,
                    reply_markup=get_cancel_kb(),
                    parse_mode=ParseMode.HTML
                )
        
        await callback.answer()
        logger.info(f'Запрос имени отправлен пользователю {callback.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в start_appointment: {e}', exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except:
            pass
        try:
            await state.clear()
        except:
            pass


# Обработчик ввода имени
@router.message(AppointmentStates.waiting_for_name)
async def process_name(message: Message, bot: Bot, state: FSMContext):
    """Обработчик ввода имени - запрашивает телефон"""
    try:
        logger.info(f'process_name: пользователь {message.from_user.id}, имя={message.text}')
        name = message.text.strip()
        
        if len(name) < 2:
            logger.warning(f'Слишком короткое имя от пользователя {message.from_user.id}: {name}')
            await message.answer(
                "❌ Имя слишком короткое. Пожалуйста, введите ваше имя еще раз:",
                reply_markup=get_cancel_kb()
            )
            return
        
        await state.update_data(client_name=name)
        await state.set_state(AppointmentStates.waiting_for_phone)
        
        text = f"✅ Имя: <b>{name}</b>\n\n"
        text += "Теперь введите ваш номер телефона или нажмите кнопку ниже, чтобы поделиться номером:"
        
        await message.answer(
            text,
            reply_markup=get_phone_kb(),
            parse_mode=ParseMode.HTML
        )
        logger.info(f'Имя принято: {name}, запрос телефона отправлен пользователю {message.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в process_name: {e}', exc_info=True)
        try:
            await message.answer("Произошла ошибка. Попробуйте еще раз.")
        except:
            pass
        try:
            await state.clear()
        except:
            pass


# Обработчик получения контакта (кнопка "Поделиться телефоном")
@router.message(AppointmentStates.waiting_for_phone, F.contact)
async def process_contact(message: Message, bot: Bot, state: FSMContext):
    """Обработчик получения контакта через кнопку"""
    try:
        logger.info(f'process_contact: пользователь {message.from_user.id}, контакт получен')
        contact: Contact = message.contact
        
        if not contact.phone_number:
            logger.warning(f'Контакт без номера телефона от пользователя {message.from_user.id}')
            await message.answer(
                "❌ Не удалось получить номер телефона. Пожалуйста, введите номер вручную:",
                reply_markup=get_phone_kb()
            )
            return
        
        phone = contact.phone_number
        logger.info(f'Номер телефона из контакта: {phone}')
        
        # Используем тот же обработчик для отправки заявки
        await process_phone_internal(message, bot, state, phone)
        
    except Exception as e:
        logger.error(f'Ошибка в process_contact: {e}', exc_info=True)
        try:
            await message.answer("Произошла ошибка. Попробуйте еще раз.", reply_markup=get_phone_kb())
        except:
            pass


# Обработчик ввода телефона (текстовый ввод)
@router.message(AppointmentStates.waiting_for_phone)
async def process_phone(message: Message, bot: Bot, state: FSMContext):
    """Обработчик ввода телефона - отправляет заявку в канал"""
    try:
        # Проверяем, не является ли это контактом (обрабатывается отдельным обработчиком)
        if message.contact:
            return
        
        logger.info(f'process_phone: пользователь {message.from_user.id}, телефон={message.text}')
        phone = message.text.strip()
        
        # Обработка кнопки "Отменить" из ReplyKeyboard
        if phone.lower() in ['отменить', '❌ отменить', 'cancel']:
            await cancel_appointment_text(message, bot, state)
            return
        
        # Простая валидация телефона
        phone_clean = re.sub(r'[^\d+]', '', phone)
        if len(phone_clean) < 10:
            logger.warning(f'Некорректный телефон от пользователя {message.from_user.id}: {phone}')
            await message.answer(
                "❌ Номер телефона некорректный. Пожалуйста, введите номер еще раз или нажмите кнопку ниже:",
                reply_markup=get_phone_kb()
            )
            return
        
        await process_phone_internal(message, bot, state, phone)
        
    except Exception as e:
        logger.error(f'Ошибка в process_phone: {e}', exc_info=True)
        try:
            await message.answer("Произошла ошибка. Попробуйте еще раз.", reply_markup=get_phone_kb())
        except:
            pass
        try:
            await state.clear()
        except:
            pass


# Внутренняя функция для обработки телефона и отправки заявки
async def process_phone_internal(message: Message, bot: Bot, state: FSMContext, phone: str):
    """Внутренняя функция для обработки телефона и отправки заявки"""
    try:
        
        # Получаем данные из состояния
        data = await state.get_data()
        doctor_name = data.get('doctor_name', 'Не указан')
        client_name = data.get('client_name', 'Не указано')
        logger.info(f'Данные заявки: врач={doctor_name}, клиент={client_name}, телефон={phone}')
        
        # Формируем сообщение для канала
        appointment_text = f"""📋 <b>Новая заявка на запись</b>

👨‍⚕️ Врач: {doctor_name}
👤 Клиент: {client_name}
📞 Телефон: {phone}
🕐 Время заявки: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"""
        
        # Отправляем заявку в канал (используем GROUP_ID из конфига)
        try:
            channel_id = conf.tg_bot.GROUP_ID
            await bot.send_message(
                chat_id=channel_id,
                text=appointment_text,
                parse_mode=ParseMode.HTML
            )
            
            # Подтверждаем пользователю
            success_text = f"""✅ <b>Заявка успешно отправлена!</b>

👨‍⚕️ Врач: {doctor_name}
👤 Ваше имя: {client_name}
📞 Ваш телефон: {phone}

Мы свяжемся с вами в ближайшее время."""
            
            # Убираем клавиатуру с кнопкой телефона
            await message.answer(
                success_text,
                reply_markup=ReplyKeyboardRemove(),
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                "Главное меню:",
                reply_markup=get_main_menu_kb()
            )
            
            logger.info(f"Заявка отправлена: врач={doctor_name}, клиент={client_name}, телефон={phone}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки заявки в канал: {e}", exc_info=True)
            await message.answer(
                "❌ Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позже или свяжитесь с нами по телефону.",
                reply_markup=ReplyKeyboardRemove()
            )
            await message.answer(
                "Главное меню:",
                reply_markup=get_main_menu_kb()
            )
        
        # Очищаем состояние
        await state.clear()
        logger.info(f'Состояние FSM очищено для пользователя {message.from_user.id}')
        
    except Exception as e:
        logger.error(f'Ошибка в process_phone_internal: {e}', exc_info=True)
        try:
            await message.answer("Произошла ошибка. Попробуйте еще раз.", reply_markup=get_phone_kb())
        except:
            pass
        try:
            await state.clear()
        except:
            pass


# Обработчик текстовой команды "Отменить" из ReplyKeyboard
async def cancel_appointment_text(message: Message, bot: Bot, state: FSMContext):
    """Обработчик отмены записи через текстовую команду"""
    try:
        logger.info(f'cancel_appointment_text: пользователь {message.from_user.id}')
        await state.clear()
        
        welcome_text = """Здравствуй, королевский друг ROYAL Clinic. 
Приглашаем вас в волшебный научный мир счастливого родительства!"""
        
        await message.answer(
            welcome_text,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.HTML
        )
        await message.answer(
            "Главное меню:",
            reply_markup=get_main_menu_kb()
        )
        logger.info(f'Запись отменена пользователем {message.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в cancel_appointment_text: {e}', exc_info=True)
        try:
            await state.clear()
        except:
            pass


# Обработчик отмены записи
@router.callback_query(F.data == "cancel_appointment")
async def cancel_appointment(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Обработчик отмены записи на прием"""
    try:
        logger.info(f'cancel_appointment: пользователь {callback.from_user.id}')
        await state.clear()
        
        welcome_text = """Здравствуй, королевский друг ROYAL Clinic. 
Приглашаем вас в волшебный научный мир счастливого родительства!"""
        
        try:
            await callback.message.edit_text(
                welcome_text,
                reply_markup=get_main_menu_kb(),
                parse_mode=ParseMode.HTML
            )
        except Exception as edit_error:
            # Если не удалось отредактировать (например, сообщение с фото), отправляем новое
            logger.warning(f'Не удалось отредактировать сообщение при отмене, отправляем новое: {edit_error}')
            await callback.message.answer(
                welcome_text,
                reply_markup=get_main_menu_kb(),
                parse_mode=ParseMode.HTML
            )
        
        await callback.answer("Запись отменена")
        logger.info(f'Запись отменена пользователем {callback.from_user.id}')
    except Exception as e:
        logger.error(f'Ошибка в cancel_appointment: {e}', exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except:
            pass
        try:
            await state.clear()
        except:
            pass


@router.message(F.chat.type == 'private')
async def echo(message: Message, bot: Bot, state: FSMContext, *args, **kwargs):
    try:
        # Проверяем, не находится ли пользователь в состоянии FSM
        current_state = await state.get_state()
        if current_state:
            # Если пользователь в состоянии FSM, не обрабатываем сообщение здесь
            # (FSM обработчики имеют приоритет)
            return
        
        # Проверяем наличие текста в сообщении
        if not message.text:
            return
        
        logger.info(f'Прочитал сообщение в личке {message.chat.id}')
        numbers = re.findall(r'➡️\s*₫\s*([\d\s]+)', message.text)
        # Убираем пробелы в числах, потом форматируем обратно с пробелами между разрядами
        formatted = [f"{int(n.replace(' ', '')):,}".replace(",", " ") for n in numbers[:3]]
        logger.info(formatted)
        if formatted:
            new_text = f"""<b>Друзья </b><tg-emoji emoji-id="5442678635909621223">❤️</tg-emoji><b>
    к</b>оманда группы 
    <i>Кто летит?📦Вьетнам!</i>
     рада представить вам сервис <a href="https://t.me/KREXPEXexchange"><i>ОБМЕНА ВАЛЮТЫ</i></a><b>
     </b><tg-emoji emoji-id="5472030678633684592">💸</tg-emoji><b> </b><i>в городе Нячанг</i>

    <b><i>ВАШ ЛУЧШИЙ КУРС </i></b>

    <tg-emoji emoji-id="5265122991380897957">💸</tg-emoji><b>1       </b><tg-emoji emoji-id="5379894627883032944">➡️</tg-emoji>   <b>₫ {formatted[0]}
    </b><tg-emoji emoji-id="5409048419211682843">💵</tg-emoji><b>1       </b><tg-emoji emoji-id="5379894627883032944">➡️</tg-emoji><b>  </b> <b>₫</b> <b>{formatted[1]}
    </b><tg-emoji emoji-id="5264945652181247629">💸</tg-emoji><b>1       </b><tg-emoji emoji-id="5379894627883032944">➡️</tg-emoji>   <b>₫</b> <b>{formatted[2]}

    </b><tg-emoji emoji-id="5217497254381754877">✅</tg-emoji> <i>от ₽20 000 - бесплатная доставка</i>
    <tg-emoji emoji-id="5217497254381754877">✅</tg-emoji> <i>от ₽100 000 - курс еще приятней</i>
    <tg-emoji emoji-id="5217497254381754877">✅</tg-emoji> <i>все сделки при личной встрече</i>
    <tg-emoji emoji-id="5217497254381754877">✅</tg-emoji> <i>другие уникальные услуги</i>

    <a href="https://t.me/KREXPEXexchange"><i>https://t.me/KREXPEXexchange</i></a>

    <tg-emoji emoji-id="5442678635909621223">❤️</tg-emoji>Мы дорожим нашим комьюнити, по этой причине делаем все, чтобы вы получали первоклассный сервис!"""
            new_text = f"""Друзья ❤️
    команда группы 
    <i>Кто летит?📦Вьетнам!</i>
    рада представить вам сервис    ОБМЕНА ВАЛЮТЫ (https://t.me/KREXPEXexchange) 💸
    в городе Нячанг

    <b><i>ВАШ ЛУЧШИЙ КУРС </i></b>

    1 <code>rub   </code>➡️   ₫ {formatted[0]}
    1 <code>usd   </code>➡️   ₫ {formatted[1]}
    1 <code>usdt  </code>➡️   ₫ {formatted[2]}

    ✅ от ₽20 000 - бесплатная доставка
    ✅ от ₽100 000 - курс еще приятней
    ✅ все сделки при личной встрече
    ✅ другие уникальные услуги

    https://t.me/KREXPEXexchange

    ❤️Мы дорожим нашим комьюнити, по этой причине делаем все, чтобы вы получали первоклассный сервис!"""

            await send_telegram_message(chat_id=message.chat.id, text=new_text)

    except Exception as e:
        logger.error(e, exc_info=True)

@router.message()
async def echo(message: Message, bot: Bot, *args, **kwargs):
    logger.debug(f'echo {message.text}')
