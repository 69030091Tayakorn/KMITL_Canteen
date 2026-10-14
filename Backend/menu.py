

def check_selection(shop_name, dish_count, selected_dishes, menu_data):
    curry_shops, menus, shop_options = menu_data
    shop = curry_shops[shop_name]
    if dish_count not in shop["prices"]:
        return "กรุณาเลือกราด 1 อย่าง หรือ 2 อย่าง"
    if len(selected_dishes) != dish_count:
        return f"กรุณาเลือกกับข้าวให้ครบ {dish_count} อย่าง"
    if len(set(selected_dishes)) != dish_count:
        return "กรุณาเลือกกับข้าวไม่ซ้ำกัน"
    for dish in selected_dishes:
        if dish not in shop["dishes"]:
            return "ไม่พบกับข้าวที่เลือกในร้านนี้"
    return ""


def calculate_price(shop_name, menu_name, dish_count=1, extra_rice=False, selected_options=None, *, menu_data):
    curry_shops, menus, shop_options = menu_data
    # คืนราคาต่อหนึ่งจาน ส่วนจำนวนจานให้ตะกร้าคำนวณ
    if shop_name in curry_shops:
        shop = curry_shops[shop_name]
        price = shop["prices"][dish_count]
        if extra_rice:
            price += shop["extra_rice_price"]
        return price
    price = menus[shop_name][menu_name]
    if selected_options:
        for group_name, choice in selected_options.items():
            price += shop_options[shop_name][group_name][choice]
    return price
