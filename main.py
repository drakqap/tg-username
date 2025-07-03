import asyncio
import logging
import threading
import json
import os
import requests
import time
import random
import string
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

# Создание Flask приложения для предотвращения засыпания
app = Flask(__name__)

@app.route('/')
def home():
    return "🔍 Username Hunter Bot работает! 🚀"

@app.route('/status')
def status():
    return {"status": "active", "bot": "username_hunter_bot"}

@app.route('/ping')
def ping():
    return {"ping": "pong", "time": time.time()}

# Функция для поддержания активности
def keep_alive():
    while True:
        try:
            # Замени на твой реальный URL Render после деплоя
            requests.get("https://your-app-name.onrender.com/ping", timeout=10)
        except:
            pass
        time.sleep(300)  # Пинг каждые 5 минут

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Константы
ADMIN_ID = 6174872743
BOT_TOKEN = "8057236237:AAFhHS9eOuyyTzd71t-H2cxB4pYPbv4d21M"
CHANNEL_ID = -1002869714443

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояние поиска
search_active = False
search_task = None

# Генераторы юзернеймов
def generate_pattern_usernames():
    """Генерирует паттерны с повторами и симметрией"""
    patterns = []
    letters = string.ascii_lowercase
    
    # Паттерны с повторами (5 символов)
    for _ in range(20):
        char1 = random.choice(letters)
        char2 = random.choice(letters)
        char3 = random.choice(letters)
        
        # Разные типы паттернов
        pattern_types = [
            char1 + char2 + char1 + char2 + char1,  # ababa
            char1 + char1 + char2 + char2 + char2,  # aabbb  
            char1 + char2 + char2 + char2 + char1,  # abbba
            char1 + char1 + char2 + char1 + char1,  # aabaa
            char1 + char2 + char3 + char3 + char3,  # abccc
            char1 + char1 + char1 + char2 + char2,  # aaabb
            char1 + char2 + char1 + char1 + char1,  # abaaa
            char1 + char1 + char2 + char2 + char1,  # aabba
        ]
        
        patterns.extend(random.sample(pattern_types, 3))
    
    # Палиндромы (5 символов)
    for _ in range(15):
        char1 = random.choice(letters)
        char2 = random.choice(letters)
        char3 = random.choice(letters)
        
        palindrome_types = [
            char1 + char2 + char3 + char2 + char1,  # abcba
            char1 + char1 + char2 + char1 + char1,  # aabaa
            char1 + char2 + char2 + char2 + char1,  # abbba
            char1 + char1 + char1 + char1 + char1,  # aaaaa
        ]
        
        patterns.extend(random.sample(palindrome_types, 2))
    
    # Числа в паттернах
    for _ in range(10):
        char = random.choice(letters)
        num = random.choice('0123456789')
        
        number_patterns = [
            char + num + char + num + char,  # a1a1a
            char + char + num + char + char,  # aa1aa
            char + num + num + num + char,   # a111a
            char + char + char + num + num,  # aaa11
            char + num + char + char + char, # a1aaa
        ]
        
        patterns.extend(random.sample(number_patterns, 2))
    
    return patterns

def generate_meme_usernames():
    """Генерирует мемные и эстетичные юзернеймы"""
    # Базовые мемные слова для генерации
    meme_bases = ["slay", "drip", "base", "ezw", "xdd", "sus", "npc", "sig", "cring", "pog", "kek", "omg", "lmao", "bro", "yik", "okay", "vibe", "mood", "fact", "true", "real", "dead", "fire", "icy", "hot", "cool", "epic", "lic", "lit", "bust", "thic", "chon"]
    
    # Окончания для удлинения
    endings = ["y", "yy", "yyy", "z", "zz", "x", "xx", "d", "dd", "s", "ss", "e", "ee", "g", "gg", "p", "pp", "w", "ww", "t", "tt", "n", "nn", "c", "cc", "k", "kk", "l", "ll", "m", "mm", "r", "rr"]
    
    variations = []
    for _ in range(30):
        base = random.choice(meme_bases)
        ending = random.choice(endings)
        
        # Создаем слово длиной 5+ символов
        if len(base) >= 5:
            variations.append(base[:5])
        elif len(base) == 4:
            variations.append(base + ending[0])
        elif len(base) == 3:
            variations.append(base + ending)
        else:
            variations.append(base + ending + random.choice('xyz'))
    
    return variations

def generate_english_russian_usernames():
    """Генерирует русские слова в английской раскладке"""
    # Русские корни для генерации
    russian_roots = [
        "si", "vz", "ot", "ub", "po", "zn", "mo", "ho", "bu", "de", "id", "ed", "le", "be", "po", "ta", "ig", "ch", "pi", "go", "sl", "vi", "sm", "pl", "kr"
    ]
    
    # Окончания на английской раскладке
    endings = ["al", "el", "il", "ol", "ul", "aj", "ej", "ij", "oj", "uj", "an", "en", "in", "on", "un", "at", "et", "it", "ot", "ut", "ay", "ey", "iy", "oy", "uy", "sh", "ch", "th", "ph", "kh"]
    
    variations = []
    for _ in range(25):
        root = random.choice(russian_roots)
        ending = random.choice(endings)
        
        # Создаем слово 5+ символов
        word = root + ending
        if len(word) >= 5:
            variations.append(word[:6])  # Максимум 6 символов
        else:
            variations.append(word + random.choice('l'))
    
    return variations

def generate_brand_usernames():
    """Генерирует бренды и известные названия"""
    # Части брендов для комбинирования
    brand_parts = [
        "app", "guc", "dio", "tes", "nvi", "tik", "dis", "net", "spo", "chr", "xbo", "ste", "twi", "red", "git", "goo", "ama", "pay", "mas", "vis", "mcd", "kfc", "piz", "coc", "pep", "sta", "mer", "bmw", "aud", "toy"
    ]
    
    # Окончания для брендов
    brand_endings = ["le", "ci", "or", "la", "dia", "tok", "ord", "flix", "ify", "ome", "xx", "am", "ch", "dit", "hub", "gle", "zon", "pal", "ter", "sa", "ks", "za", "ola", "si", "ks", "des", "w", "di", "ta"]
    
    variations = []
    for _ in range(25):
        part = random.choice(brand_parts)
        ending = random.choice(brand_endings)
        
        # Создаем бренд 5+ символов
        brand = part + ending
        if len(brand) >= 5:
            variations.append(brand[:7])  # Максимум 7 символов
        else:
            variations.append(brand + random.choice('xy'))
    
    return variations

def generate_all_usernames():
    """Генерирует все типы юзернеймов"""
    all_usernames = []
    
    # Основные типы
    all_usernames.extend(generate_pattern_usernames())
    all_usernames.extend(generate_meme_usernames()) 
    all_usernames.extend(generate_english_russian_usernames())
    all_usernames.extend(generate_brand_usernames())
    
    # Дополнительные креативные типы
    all_usernames.extend(generate_random_combinations())
    all_usernames.extend(generate_aesthetic_usernames())
    all_usernames.extend(generate_gaming_usernames())
    
    # Убираем дубликаты и фильтруем
    unique_usernames = list(set(all_usernames))
    
    # Фильтруем только валидные (5+ символов, начинается с буквы)
    valid_usernames = []
    for username in unique_usernames:
        if len(username) >= 5 and username[0].isalpha() and username.isalnum():
            valid_usernames.append(username)
    
    return valid_usernames

def generate_random_combinations():
    """Генерирует случайные комбинации букв и цифр"""
    combinations = []
    letters = string.ascii_lowercase
    
    for _ in range(20):
        # Случайные комбинации 5-6 символов
        combo_types = [
            # Буква + цифры + буква
            random.choice(letters) + str(random.randint(100, 999)) + random.choice(letters),
            # Две буквы + цифры + буква
            random.choice(letters) + random.choice(letters) + str(random.randint(10, 99)) + random.choice(letters),
            # Буква + цифра + буквы
            random.choice(letters) + str(random.randint(1, 9)) + ''.join(random.choices(letters, k=3)),
            # Буквы + цифра в конце
            ''.join(random.choices(letters, k=4)) + str(random.randint(1, 9)),
            # Цифра в середине
            ''.join(random.choices(letters, k=2)) + str(random.randint(1, 9)) + ''.join(random.choices(letters, k=2)),
        ]
        
        combinations.extend(random.sample(combo_types, 2))
    
    return combinations

def generate_aesthetic_usernames():
    """Генерирует эстетичные юзернеймы"""
    aesthetics = []
    
    # Красивые сочетания звуков
    beautiful_sounds = ["ae", "ai", "ao", "au", "ea", "ei", "eo", "eu", "ia", "ie", "io", "iu", "oa", "oe", "oi", "ou", "ua", "ue", "ui", "uo"]
    consonants = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "z"]
    
    for _ in range(20):
        # Красивые комбинации
        sound = random.choice(beautiful_sounds)
        cons1 = random.choice(consonants)
        cons2 = random.choice(consonants)
        
        aesthetic_types = [
            cons1 + sound + cons2,  # bael
            sound + cons1 + cons2,  # aelb
            cons1 + sound + sound,  # baeae
            sound + cons1 + sound,  # aelae
            cons1 + cons2 + sound,  # blae
        ]
        
        for aesthetic in aesthetic_types:
            if len(aesthetic) >= 5:
                aesthetics.append(aesthetic[:6])
            else:
                aesthetics.append(aesthetic + random.choice(consonants))
    
    return aesthetics

def generate_gaming_usernames():
    """Генерирует геймерские юзернеймы"""
    gaming = []
    
    # Геймерские префиксы и суффиксы
    prefixes = ["pro", "god", "max", "top", "ace", "neo", "dark", "fire", "ice", "storm", "void", "rage", "epic", "mega", "ultra", "super", "hyper", "elite", "alpha", "beta", "gamma", "delta", "omega"]
    suffixes = ["x", "z", "er", "ly", "fy", "ty", "ry", "ny", "my", "ky", "py", "by", "gy", "dy", "wy", "sy", "cy", "vy", "hy", "jy"]
    
    for _ in range(15):
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        # Создаем геймерские ники
        gaming_types = [
            prefix + suffix,  # prox
            prefix + str(random.randint(1, 99)),  # pro99
            prefix[:2] + suffix + str(random.randint(1, 9)),  # prox9
            prefix + random.choice('xyz'),  # prox
        ]
        
        for game_nick in gaming_types:
            if len(game_nick) >= 5:
                gaming.append(game_nick[:7])
    
    return gaming

async def check_username_availability(username):
    """Проверяет доступность юзернейма"""
    try:
        # Пытаемся получить информацию о чате по username
        chat = await bot.get_chat(f"@{username}")
        return False  # Если чат найден, значит username занят
    except TelegramBadRequest:
        return True  # Если чат не найден, username свободен
    except Exception as e:
        logging.error(f"Ошибка проверки username {username}: {e}")
        return False

async def search_usernames():
    """Основная функция поиска юзернеймов"""
    global search_active
    
    while search_active:
        try:
            # Генерируем батч юзернеймов
            usernames = generate_all_usernames()
            random.shuffle(usernames)
            
            # Проверяем каждый username
            for username in usernames[:50]:  # Проверяем по 50 за раз
                if not search_active:
                    break
                    
                is_available = await check_username_availability(username)
                
                if is_available:
                    # Отправляем найденный username админу
                    await send_username_to_admin(username)
                    
                # Пауза между проверками чтобы не словить rate limit
                await asyncio.sleep(2)
            
            # Пауза между батчами
            await asyncio.sleep(10)
            
        except Exception as e:
            logging.error(f"Ошибка в поиске юзернеймов: {e}")
            await asyncio.sleep(30)

async def send_username_to_admin(username):
    """Отправляет найденный username админу"""
    try:
        text = f"""🎯 Найден свободный юзернейм: @{username}
👇 Выбери действие:"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Поставить", callback_data=f"set_{username}"),
                InlineKeyboardButton(text="❌ Не ставить", callback_data=f"skip_{username}")
            ]
        ])
        
        await bot.send_message(ADMIN_ID, text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Ошибка отправки username админу: {e}")

async def set_channel_username(username):
    """Устанавливает username для канала"""
    try:
        await bot.set_chat_username(CHANNEL_ID, username)
        return True
    except Exception as e:
        logging.error(f"Ошибка установки username {username}: {e}")
        return False

# Обработчики команд

@dp.message(Command("start"))
async def start_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ Этот бот только для администратора!")
        return
    
    start_text = """🔍 <b>Username Hunter Bot</b>

🎯 <b>Команды:</b>
• /search_start - Начать поиск юзернеймов
• /search_stop - Остановить поиск
• /search_status - Статус поиска
• /generate - Сгенерировать примеры юзернеймов

<b>Бот автоматически ищет свободные юзернеймы для канала и отправляет их тебе!</b>"""
    
    await message.reply(start_text, parse_mode="HTML")

@dp.message(Command("search_start"))
async def search_start_handler(message: Message):
    global search_active, search_task
    
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ Недостаточно прав!")
        return
    
    if search_active:
        await message.reply("⚠️ Поиск уже запущен!")
        return
    
    search_active = True
    search_task = asyncio.create_task(search_usernames())
    
    await message.reply("🚀 <b>Поиск юзернеймов запущен!</b>\n\nБот начал сканировать свободные юзернеймы. Как только найдет что-то интересное - пришлет тебе!", parse_mode="HTML")

@dp.message(Command("search_stop"))
async def search_stop_handler(message: Message):
    global search_active, search_task
    
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ Недостаточно прав!")
        return
    
    if not search_active:
        await message.reply("⚠️ Поиск не запущен!")
        return
    
    search_active = False
    if search_task:
        search_task.cancel()
    
    await message.reply("⏹️ <b>Поиск остановлен!</b>", parse_mode="HTML")

@dp.message(Command("search_status"))
async def search_status_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ Недостаточно прав!")
        return
    
    status = "🟢 Активен" if search_active else "🔴 Остановлен"
    await message.reply(f"📊 <b>Статус поиска:</b> {status}", parse_mode="HTML")

@dp.message(Command("generate"))
async def generate_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ Недостаточно прав!")
        return
    
    # Генерируем примеры всех типов
    patterns = generate_pattern_usernames()[:8]
    memes = generate_meme_usernames()[:8]
    russian = generate_english_russian_usernames()[:8]
    brands = generate_brand_usernames()[:8]
    combinations = generate_random_combinations()[:8]
    aesthetics = generate_aesthetic_usernames()[:8]
    gaming = generate_gaming_usernames()[:8]
    
    text = f"""🎲 <b>Примеры генерируемых юзернеймов:</b>

🔄 <b>Паттерны:</b>
{', '.join(patterns)}

😎 <b>Мемы:</b>
{', '.join(memes)}

🇷🇺 <b>Русские слова:</b>
{', '.join(russian)}

🏷️ <b>Бренды:</b>
{', '.join(brands)}

🎯 <b>Комбинации:</b>
{', '.join(combinations)}

✨ <b>Эстетичные:</b>
{', '.join(aesthetics)}

🎮 <b>Геймерские:</b>
{', '.join(gaming)}

<i>Всего типов: 7. Каждый запуск генерирует новые уникальные варианты!</i>"""
    
    await message.reply(text, parse_mode="HTML")

# Обработчики кнопок

@dp.callback_query(lambda c: c.data.startswith("set_"))
async def set_username_callback(callback_query: CallbackQuery):
    username = callback_query.data.replace("set_", "")
    
    await callback_query.message.edit_text(f"⏳ Устанавливаю username @{username}...")
    
    success = await set_channel_username(username)
    
    if success:
        await callback_query.message.edit_text(f"✅ <b>Username @{username} успешно установлен!</b>", parse_mode="HTML")
    else:
        await callback_query.message.edit_text(f"❌ <b>Ошибка установки @{username}</b>\n\nВозможно username уже занят или есть ограничения.", parse_mode="HTML")
    
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("skip_"))
async def skip_username_callback(callback_query: CallbackQuery):
    username = callback_query.data.replace("skip_", "")
    
    await callback_query.message.edit_text(f"⏭️ Username @{username} пропущен")
    await callback_query.answer()

# Главная функция
async def main():
    print("🔍 Username Hunter Bot запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запуск Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запуск keep-alive в отдельном потоке
    keep_alive_thread = threading.Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()
    
    # Запуск бота
    asyncio.run(main())
