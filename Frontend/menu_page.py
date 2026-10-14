from functools import partial

import customtkinter as ctk

from Backend import menu, catalog


class MenuPage(ctk.CTkFrame):
    """หน้าเลือกอาหาร รับคำสั่งเพิ่มตะกร้าและย้อนกลับจากหน้าต่างหลัก"""

    def __init__(self, parent, canteen_name, shop_name, add_to_cart, go_back):
        super().__init__(parent, fg_color="transparent")
        self.shop_name = shop_name
        self.canteen_name = canteen_name
        self.add_to_cart = add_to_cart
        self.go_back = go_back
        self.show_menu_list()

    def clear_content(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_menu_list(self):
        self.clear_content()
        self.menu_data = catalog.get_menu_data(self.canteen_name, self.shop_name)
        self.curry_shops, self.menus, self.shop_options = self.menu_data
        ctk.CTkLabel(self, text="เมนูและราคาตัวอย่างจาก SQLite").pack(pady=8)
        if self.shop_name in self.curry_shops:
            prices = self.curry_shops[self.shop_name]["prices"]
            dishes = self.curry_shops[self.shop_name]["dishes"]
            if not prices or not dishes:
                ctk.CTkLabel(self, text="วันนี้ยังไม่มีเมนูพร้อมขาย").pack(pady=8)
                ctk.CTkButton(self, text="กลับไปเลือกร้าน", command=self.go_back).pack(pady=8)
                return
            price = min(prices.values())
            ctk.CTkButton(
                self, text=f"ข้าวราดแกง — เริ่มต้น {price} บาท", height=48,
                command=partial(self.show_menu_details, "ข้าวราดแกง"),
            ).pack(fill="x", pady=8)
        else:
            if not self.menus[self.shop_name]:
                ctk.CTkLabel(self, text="วันนี้ยังไม่มีเมนูพร้อมขาย").pack(pady=8)
            for menu_name, price in self.menus[self.shop_name].items():
                ctk.CTkButton(
                    self, text=f"{menu_name} — เริ่มต้น {price} บาท", height=48,
                    command=partial(self.show_menu_details, menu_name),
                ).pack(fill="x", pady=8)
        ctk.CTkButton(self, text="กลับไปเลือกร้าน", command=self.go_back).pack(pady=12)

    def show_menu_details(self, menu_name):
        self.clear_content()
        ctk.CTkButton(self, text="กลับไปเลือกเมนู", command=self.show_menu_list).pack(pady=8)
        ctk.CTkLabel(self, text=menu_name, font=ctk.CTkFont(size=22, weight="bold")).pack(pady=8)
        if self.shop_name in self.curry_shops:
            self.show_curry_options()
        else:
            self.show_regular_menu(menu_name)

        self.message_label = ctk.CTkLabel(self, text="", wraplength=500)
        self.message_label.pack(pady=8)
        ctk.CTkButton(self, text="กลับไปเลือกเมนู", command=self.show_menu_list).pack(pady=12)

    def show_regular_menu(self, menu_name):
        # แยกตัวเลือกของแต่ละเมนู ไม่ให้การเลือกจานหนึ่งกระทบอีกจาน
        self.menu_choices = {}
        self.menu_price_labels = {}
        price = menu.calculate_price(self.shop_name, menu_name, menu_data=self.menu_data)
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=8)
        ctk.CTkLabel(frame, text=f"{menu_name} — {price} บาท").pack(pady=8)
        self.menu_choices[menu_name] = {}
        for group_name, choices in self.shop_options.get(self.shop_name, {}).items():
            ctk.CTkLabel(frame, text=group_name).pack(pady=(8, 0))
            first_choice = list(choices)[0]
            choice_variable = ctk.StringVar(value=first_choice)
            self.menu_choices[menu_name][group_name] = choice_variable
            for choice, extra_price in choices.items():
                choice_text = choice
                if extra_price > 0:
                    choice_text += f" (+{extra_price} บาท)"
                ctk.CTkRadioButton(
                    frame,
                    text=choice_text,
                    variable=choice_variable,
                    value=choice,
                    command=partial(self.update_regular_price, menu_name),
                ).pack(pady=4)

        price_label = ctk.CTkLabel(frame, text=f"ราคาต่อรายการ {price} บาท")
        price_label.pack(pady=8)
        self.menu_price_labels[menu_name] = price_label
        note_entry = ctk.CTkEntry(frame, placeholder_text="หมายเหตุถึงร้าน (ไม่บังคับ)", width=300)
        note_entry.pack(pady=4)
        ctk.CTkButton(
            frame, text="เพิ่มลงตะกร้า",
            command=partial(self.add_regular_item, menu_name, note_entry),
        ).pack(pady=8)

    def get_selected_options(self, menu_name):
        selected_options = {}
        for group_name, choice_variable in self.menu_choices[menu_name].items():
            selected_options[group_name] = choice_variable.get()
        return selected_options

    def update_regular_price(self, menu_name):
        selected_options = self.get_selected_options(menu_name)
        price = menu.calculate_price(self.shop_name, menu_name, selected_options=selected_options, menu_data=self.menu_data)
        self.menu_price_labels[menu_name].configure(text=f"ราคาต่อรายการ {price} บาท")

    def add_regular_item(self, menu_name, note_entry):
        selected_options = self.get_selected_options(menu_name)
        price = menu.calculate_price(self.shop_name, menu_name, selected_options=selected_options, menu_data=self.menu_data)
        options = []
        for group_name, choice in selected_options.items():
            options.append(f"{group_name}: {choice}")
        self.add_to_cart(menu_name, price, options, note_entry.get())
        self.message_label.configure(text=f"เพิ่ม {menu_name} ลงตะกร้าแล้ว")

    def show_curry_options(self):
        shop = self.curry_shops[self.shop_name]
        self.dish_count = ctk.IntVar(value=min(shop["prices"]))
        for count, price in shop["prices"].items():
            ctk.CTkRadioButton(
                self, text=f"ราด {count} อย่าง — {price} บาท",
                variable=self.dish_count, value=count, command=self.update_price,
            ).pack(pady=6)

        ctk.CTkLabel(self, text="เลือกกับข้าวให้ครบตามจำนวนที่กำหนด").pack(pady=8)
        self.dish_choices = {}
        for dish in shop["dishes"]:
            choice = ctk.BooleanVar(value=False)
            self.dish_choices[dish] = choice
            ctk.CTkCheckBox(self, text=dish, variable=choice).pack(pady=6)

        self.extra_rice = ctk.BooleanVar(value=False)
        rice_text = "เพิ่มข้าว"
        if shop["extra_rice_price"] > 0:
            rice_text += f" (+{shop['extra_rice_price']} บาท)"
        ctk.CTkCheckBox(
            self, text=rice_text,
            variable=self.extra_rice, command=self.update_price,
            state="normal" if shop.get("extra_rice_available") else "disabled",
        ).pack(pady=12)
        self.note_entry = ctk.CTkEntry(self, placeholder_text="หมายเหตุ เช่น แยกน้ำแกง", width=300)
        self.note_entry.pack(pady=8)
        self.price_label = ctk.CTkLabel(self, text="")
        self.price_label.pack(pady=8)
        self.update_price()
        ctk.CTkButton(self, text="เพิ่มลงตะกร้า", command=self.add_curry_item).pack(pady=8)

    def update_price(self):
        price = menu.calculate_price(
            self.shop_name, "ข้าวราดแกง", self.dish_count.get(), self.extra_rice.get(), menu_data=self.menu_data,
        )
        self.price_label.configure(text=f"ราคาต่อจาน {price} บาท")

    def add_curry_item(self):
        selected_dishes = []
        for dish, choice in self.dish_choices.items():
            if choice.get():
                selected_dishes.append(dish)

        count = self.dish_count.get()
        error = menu.check_selection(self.shop_name, count, selected_dishes, self.menu_data)
        if error:
            self.message_label.configure(text=error)
            return

        price = menu.calculate_price(self.shop_name, "ข้าวราดแกง", count, self.extra_rice.get(), menu_data=self.menu_data)
        options = selected_dishes.copy()
        if self.extra_rice.get():
            options.append("เพิ่มข้าว")
        self.add_to_cart(f"ข้าวราดแกง {count} อย่าง", price, options, self.note_entry.get())
        self.message_label.configure(text="เพิ่มข้าวราดแกงลงตะกร้าแล้ว")
