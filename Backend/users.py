import hashlib
import hmac
import secrets
import sqlite3

from Backend import database


_current_user_id = None


def hash_password(password):
    salt = secrets.token_hex(16)
    rounds = 600000
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), rounds)
    return f'{rounds}${salt}${digest.hex()}'


def check_password(password, saved_hash):
    try:
        rounds, salt, expected = saved_hash.split('$')
        rounds = int(rounds)
        if rounds != 600000:
            return False
        digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), rounds)
        return hmac.compare_digest(digest.hex(), expected)
    except (ValueError, TypeError, AttributeError):
        return False


def create_account(username, password, display_name, role, shop_id=None):
    username = username.strip()
    display_name = display_name.strip()
    if not 3 <= len(username) <= 40:
        raise ValueError('ชื่อผู้ใช้ต้องมี 3–40 ตัวอักษร')
    if not 8 <= len(password) <= 128:
        raise ValueError('รหัสผ่านต้องมี 8–128 ตัวอักษร')
    if not display_name or len(display_name) > 100:
        raise ValueError('กรุณากรอกชื่อแสดงไม่เกิน 100 ตัวอักษร')
    if role not in ('customer', 'shop'):
        raise ValueError('ประเภทบัญชีไม่ถูกต้อง')
    password_hash = hash_password(password)
    connection = database.connect_database()
    try:
        with connection:
            cursor = connection.execute('''
                INSERT INTO users(username, password_hash, display_name, role, shop_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, display_name, role, shop_id))
        return cursor.lastrowid
    except sqlite3.IntegrityError as error:
        raise ValueError('ชื่อผู้ใช้ซ้ำ หรือข้อมูลร้านไม่ถูกต้อง') from error
    finally:
        connection.close()


def register_customer(username, password, display_name):
    return create_account(username, password, display_name, 'customer')


def login(username, password):
    global _current_user_id
    logout()
    connection = database.connect_database()
    connection.row_factory = sqlite3.Row
    try:
        user = connection.execute('SELECT * FROM users WHERE username = ?', (username.strip(),)).fetchone()
    finally:
        connection.close()
    if user is None or not check_password(password, user['password_hash']):
        raise ValueError('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    _current_user_id = user['user_id']
    return require_user()


def logout():
    global _current_user_id
    _current_user_id = None


def require_user(role=None):
    if _current_user_id is None:
        raise ValueError('กรุณาเข้าสู่ระบบก่อน')
    connection = database.connect_database()
    connection.row_factory = sqlite3.Row
    try:
        user = connection.execute('''
            SELECT user_id, username, display_name, role, shop_id
            FROM users WHERE user_id = ?
        ''', (_current_user_id,)).fetchone()
    finally:
        connection.close()
    if user is None or (role is not None and user['role'] != role):
        raise ValueError('บัญชีนี้ไม่มีสิทธิ์ใช้งานส่วนนี้')
    return dict(user)


def get_my_shop():
    user = require_user('shop')
    connection = database.connect_database()
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute('''
            SELECT shops.shop_id, shops.name AS shop_name, canteens.name AS canteen_name
            FROM shops JOIN canteens USING(canteen_id) WHERE shops.shop_id = ?
        ''', (user['shop_id'],)).fetchone()
        if row is None:
            raise ValueError('ไม่พบร้านที่ผูกกับบัญชีนี้')
        return dict(row)
    finally:
        connection.close()
