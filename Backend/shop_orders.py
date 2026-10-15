import sqlite3

from Backend import database, users


status_names = {
    'pending': 'ออเดอร์เก่า — ยังไม่ผ่านขั้นแจ้งชำระ',
    'awaiting_payment_review': 'รอตรวจสอบการชำระเงิน',
    'payment_rejected': 'หลักฐานชำระไม่ผ่าน',
    'paid': 'ตรวจรับเงินแล้ว รอร้านรับออเดอร์',
    'preparing': 'กำลังเตรียมอาหาร',
    'ready': 'พร้อมรับอาหาร',
    'completed': 'รับอาหารแล้ว',
}

next_statuses = {
    'awaiting_payment_review': ('paid', 'payment_rejected'),
    'payment_rejected': ('awaiting_payment_review',),
    'paid': ('preparing',),
    'preparing': ('ready',),
    'ready': ('completed',),
}


def read_orders(canteen_name, shop_name):
    user = users.require_user('shop')
    connection = database.connect_database()
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute("""
            SELECT orders.*, COALESCE(SUM(unit_price * quantity), 0) AS total
            FROM orders LEFT JOIN order_items USING(order_id)
            WHERE canteen_name = ? AND shop_name = ? AND orders.shop_id = ?
            GROUP BY orders.order_id ORDER BY orders.order_id DESC
        """, (canteen_name, shop_name, user['shop_id']))
        return [dict(row) for row in rows]
    finally:
        connection.close()


def read_items(order_id, canteen_name, shop_name):
    user = users.require_user('shop')
    connection = database.connect_database()
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute("""
            SELECT order_items.* FROM order_items
            JOIN orders USING(order_id)
            WHERE order_id = ? AND canteen_name = ? AND shop_name = ? AND orders.shop_id = ?
            ORDER BY item_id
        """, (order_id, canteen_name, shop_name, user['shop_id']))
        return [dict(row) for row in rows]
    finally:
        connection.close()


def change_status(order_id, canteen_name, shop_name, old_status, new_status):
    if new_status not in next_statuses.get(old_status, ()):
        raise ValueError('ไม่สามารถข้ามขั้นตอนหรือย้อนสถานะนี้ได้')
    user = users.require_user('shop')
    connection = database.connect_database()
    try:
        with connection:
            cursor = connection.execute("""
                UPDATE orders SET status = ?
                WHERE order_id = ? AND canteen_name = ? AND shop_name = ? AND orders.shop_id = ? AND status = ?
            """, (new_status, order_id, canteen_name, shop_name, user['shop_id'], old_status))
            if cursor.rowcount != 1:
                raise ValueError('ไม่พบออเดอร์ของร้านนี้ หรือสถานะเปลี่ยนแล้ว กรุณารีเฟรช')
    finally:
        connection.close()
