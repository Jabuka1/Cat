import sqlite3

# Создание подключения к базе данных и таблиц
def init_db():
    conn = sqlite3.connect("cats_shop.db")
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT
        )
    ''')

    # Таблица покупок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            cat_name TEXT,
            price TEXT,
            city TEXT,
            address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица отзывов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            review_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица рефералов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,        -- кто получил реферала
            referrer_id INTEGER     -- кто пригласил
        )
    ''')

    conn.commit()
    conn.close()

# Добавляем нового пользователя
def add_user(user_id, username, full_name):
    conn = sqlite3.connect("cats_shop.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, full_name)
        VALUES (?, ?, ?)
    ''', (user_id, username, full_name))
    conn.commit()
    conn.close()

# Добавляем реферала
def add_referral(user_id, referrer_id):
    conn = sqlite3.connect("cats_shop.db")
    cursor = conn.cursor()
    # Проверка, чтобы не было дублирующих записей
    cursor.execute('''
        SELECT * FROM referrals WHERE user_id = ? AND referrer_id = ?
    ''', (user_id, referrer_id))
    if cursor.fetchone() is None:
        cursor.execute('''
            INSERT INTO referrals (user_id, referrer_id)
            VALUES (?, ?)
        ''', (user_id, referrer_id))
        conn.commit()
    conn.close()

# Получить количество рефералов по referrer_id
def get_referrals_count(referrer_id):
    conn = sqlite3.connect("cats_shop.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM referrals WHERE referrer_id = ?
    ''', (referrer_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Добавление покупки
def add_purchase(user_id, cat_name, price, city, address):
    conn = sqlite3.connect("cats_shop.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO purchases (user_id, cat_name, price, city, address)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, cat_name, price, city, address))
    conn.commit()
    conn.close()

# Получение всех покупок пользователя
def get_purchases(user_id):
    conn = sqlite3.connect("cats_shop.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cat_name, price, city, address, timestamp FROM purchases
        WHERE user_id = ?
        ORDER BY timestamp DESC
    ''', (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result

# Добавление отзыва
def add_review(user_id, review_text):
    conn = sqlite3.connect("cats_shop.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reviews (user_id, review_text)
        VALUES (?, ?)
    ''', (user_id, review_text))
    conn.commit()
    conn.close()

# Получение всех отзывов
def get_reviews():
    conn = sqlite3.connect("cats_shop.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT review_text FROM reviews
        ORDER BY timestamp DESC
    ''')
    reviews = [row[0] for row in cursor.fetchall()]
    conn.close()
    return reviews