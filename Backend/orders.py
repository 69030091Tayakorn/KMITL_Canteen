import json
from datetime import datetime

from Backend import checkout, database, catalog, users


def check_items(canteen_name, shop_name, items):
    if not items:
        raise ValueError("ตะกร้าว่าง กรุณาเพิ่มอาหารก่อน")
    for item in items:
        if item["canteen"] != canteen_name or item["shop"] != shop_name:
            raise ValueError("หนึ่งคำสั่งซื้อต้องเป็นอาหารจากร้านเดียวกัน")
        quantity = item["quantity"]
        price = item["price"]
        if type(quantity) is not int or quantity < 1:
            raise ValueError("จำนวนอาหารต้องเป็นจำนวนเต็มตั้งแต่ 1 ขึ้นไป")
        if type(price) is not int or price < 0:
            raise ValueError("ราคาอาหารต้องเป็นจำนวนเต็มบาทและไม่ติดลบ")


def insert_order(connection, canteen_name, shop_name, name, phone, pickup_date, pickup_time, user_id, shop_id):
    sql = """
        INSERT INTO orders (
            canteen_name, shop_name, customer_name, phone,
            pickup_date, pickup_time, created_at, status, user_id, shop_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    created_at = datetime.now(checkout.THAI_TIME).isoformat(timespec="seconds")
    values = (
        canteen_name,
        shop_name,
        name.strip(),
        phone.strip(),
        pickup_date,
        pickup_time,
        created_at,
        "awaiting_payment_review",
        user_id,
        shop_id,
    )
    cursor = connection.execute(sql, values)
    return cursor.lastrowid


def insert_order_item(connection, order_id, item):
    sql = """
        INSERT INTO order_items (
            order_id, menu_name, unit_price, quantity, options, note
        ) VALUES (?, ?, ?, ?, ?, ?)
    """
    options_text = json.dumps(item["options"], ensure_ascii=False)
    values = (
        order_id,
        item["menu"],
        item["price"],
        item["quantity"],
        options_text,
        item["note"],
    )
    connection.execute(sql, values)


def save_order(canteen_name, shop_name, items, name, phone, pickup_date, pickup_time):
    user = users.require_user('customer')
    shop = catalog.get_shop(canteen_name, shop_name)
    if shop is None:
        raise ValueError('ไม่พบร้านอาหารนี้')
    error = checkout.check_details(name, phone, pickup_date, pickup_time)
    if error:
        raise ValueError(error)
    check_items(canteen_name, shop_name, items)
    for item in items:
        catalog.check_cart_item(item)

    connection = database.connect_database()
    try:
        with connection:
            order_id = insert_order(
                connection, canteen_name, shop_name, name, phone,
                pickup_date, pickup_time, user['user_id'], shop['shop_id'],
            )

            for item in items:
                insert_order_item(connection, order_id, item)
        return order_id
    finally:
        connection.close()
