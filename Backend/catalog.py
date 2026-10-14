import sqlite3

from Backend import database


def read_rows(sql, values=()):
    connection = database.connect_database()
    connection.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in connection.execute(sql, values)]
    finally:
        connection.close()


def get_canteens():
    result = {}
    for row in read_rows('SELECT name FROM canteens ORDER BY canteen_id'):
        result[row['name']] = []
    rows = read_rows("""
        SELECT canteens.name AS canteen_name, shops.name AS shop_name
        FROM shops JOIN canteens USING(canteen_id) ORDER BY shops.shop_id
    """)
    for row in rows:
        result[row['canteen_name']].append(row['shop_name'])
    return result


def get_shop(canteen_name, shop_name):
    rows = read_rows("""
        SELECT shops.* FROM shops JOIN canteens USING(canteen_id)
        WHERE canteens.name = ? AND shops.name = ?
    """, (canteen_name, shop_name))
    if not rows:
        raise ValueError('ไม่พบร้านในโรงอาหารนี้')
    return rows[0]


def get_menu_items(shop_id):
    return read_rows('SELECT * FROM menu_items WHERE shop_id = ? ORDER BY menu_id', (shop_id,))


def get_menu_data(canteen_name, shop_name):
    shop = get_shop(canteen_name, shop_name)
    menus = {}
    curry = {'dishes': [], 'prices': {}, 'extra_rice_price': 0}
    for item in get_menu_items(shop['shop_id']):
        if not item['is_available']:
            continue
        kind = item['menu_type']
        if kind == 'regular':
            menus[item['name']] = item['price']
        elif kind == 'curry_dish':
            curry['dishes'].append(item['name'])
        elif kind == 'curry_price':
            curry['prices'][item['dish_count']] = item['price']
        elif kind == 'extra_rice':
            curry['extra_rice_price'] = item['price']
            curry['extra_rice_available'] = True
    options = {}
    for row in read_rows('SELECT * FROM menu_options WHERE shop_id = ? ORDER BY option_id', (shop['shop_id'],)):
        options.setdefault(row['group_name'], {})[row['name']] = row['extra_price']
    curry_shops = {shop_name: curry} if shop['shop_type'] == 'curry' else {}
    return curry_shops, {shop_name: menus}, {shop_name: options}


def check_cart_item(item):
    from Backend import menu

    data = get_menu_data(item['canteen'], item['shop'])
    curry_shops, menus, options = data
    shop_name = item['shop']
    error = 'เมนูหรือตัวเลือกหมด/เปลี่ยนราคา กรุณาลบรายการเดิมแล้วเลือกใหม่'
    try:
        if shop_name in curry_shops:
            count = None
            for number in curry_shops[shop_name]['prices']:
                if item['menu'] == f'ข้าวราดแกง {number} อย่าง':
                    count = number
            if count is None:
                raise ValueError(error)
            dishes = [name for name in item['options'] if name != 'เพิ่มข้าว']
            extra_rice = 'เพิ่มข้าว' in item['options']
            if menu.check_selection(shop_name, count, dishes, data):
                raise ValueError(error)
            if extra_rice and not curry_shops[shop_name].get('extra_rice_available'):
                raise ValueError(error)
            price = menu.calculate_price(shop_name, item['menu'], count, extra_rice, menu_data=data)
        else:
            selected = {}
            for value in item['options']:
                group, choice = value.split(': ', 1)
                if group in selected:
                    raise ValueError(error)
                selected[group] = choice
            if set(selected) != set(options[shop_name]):
                raise ValueError(error)
            price = menu.calculate_price(shop_name, item['menu'], selected_options=selected, menu_data=data)
        if price != item['price']:
            raise ValueError(error)
    except (KeyError, TypeError) as cause:
        raise ValueError(error) from cause
