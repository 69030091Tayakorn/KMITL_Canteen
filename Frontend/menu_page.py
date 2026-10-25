from functools import partial
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from Backend import menu, catalog


ORANGE = "#F45B2A"
ORANGE_HOVER = "#DF4B20"
TEXT = "#242424"
MUTED = "#777777"
BORDER = "#EAEAEA"
WHITE = "#FFFFFF"
SOFT_ORANGE = "#FBE6D9"


class MenuPage(ctk.CTkFrame):
    """หน้าร้านค้าและรายการอาหาร ใช้ layout เดียวกันกับทุกร้าน"""

    def __init__(self, parent, canteen_name, shop_name, add_to_cart, go_back):
        super().__init__(parent, fg_color="transparent")
        self.shop_name = shop_name
        self.canteen_name = canteen_name
        self.add_to_cart = add_to_cart
        self.go_back = go_back
        self.is_favorite = False
        self.menu_data = catalog.get_menu_data(self.canteen_name, self.shop_name)
        self.curry_shops, self.menus, self.shop_options = self.menu_data
        self._build_layout()
        self.show_menu_list()

    def _build_layout(self):
        # Header inside the shop page
        self.top_row = ctk.CTkFrame(self, fg_color="transparent")
        self.top_row.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(
            self.top_row, text="←", width=38, height=34, corner_radius=9,
            fg_color=WHITE, hover_color="#FFF0E9", text_color=TEXT,
            border_width=1, border_color=BORDER, command=self.go_back,
        ).pack(side="left", padx=(0, 9))
        ctk.CTkLabel(
            self.top_row, text=self.shop_name,
            font=ctk.CTkFont(size=21, weight="bold"), text_color=TEXT, anchor="w",
        ).pack(side="left", fill="x", expand=True)
        self.favorite_button = ctk.CTkButton(
            self.top_row, text="♡", width=38, height=34, corner_radius=9,
            fg_color=WHITE, hover_color="#FFF0E9", text_color=ORANGE,
            border_width=1, border_color=BORDER, font=ctk.CTkFont(size=22),
            command=self.toggle_favorite,
        )
        self.favorite_button.pack(side="right")

        self.columns = ctk.CTkFrame(self, fg_color="transparent")
        self.columns.pack(fill="x", expand=True)
        self.columns.grid_columnconfigure(0, weight=2, uniform="shop_page", minsize=250)
        self.columns.grid_columnconfigure(1, weight=3, uniform="shop_page", minsize=300)

        self.shop_info = ctk.CTkFrame(
            self.columns, fg_color=WHITE, corner_radius=14,
            border_width=1, border_color=BORDER,
        )
        self.shop_info.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        self.shop_image_area = ctk.CTkFrame(
            self.shop_info, fg_color=SOFT_ORANGE, corner_radius=10, height=150,
        )
        self.shop_image_area.pack(fill="x", padx=10, pady=(10, 8))
        self.shop_image_area.pack_propagate(False)
        shop_image = self._find_image(self.shop_name, (420, 150))
        if shop_image:
            image_label = ctk.CTkLabel(self.shop_image_area, text="", image=shop_image)
            image_label.pack(fill="both", expand=True)
            image_label.image = shop_image
        else:
            ctk.CTkLabel(
                self.shop_image_area, text="🍜", text_color=ORANGE,
                font=ctk.CTkFont(size=52),
            ).pack(expand=True)

        ctk.CTkLabel(
            self.shop_info, text=self.shop_name,
            font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT,
            anchor="w", wraplength=300,
        ).pack(fill="x", padx=12, pady=(4, 3))
        ctk.CTkLabel(
            self.shop_info, text=self.canteen_name,
            font=ctk.CTkFont(size=13), text_color=MUTED, anchor="w",
        ).pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkFrame(self.shop_info, height=1, fg_color="#F0F0F0").pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(
            self.shop_info, text="รายการอาหาร",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT, anchor="w",
        ).pack(fill="x", padx=12, pady=(6, 2))
        ctk.CTkLabel(
            self.shop_info, text="เลือกเมนูทางด้านขวาเพื่อเพิ่มลงตะกร้า",
            font=ctk.CTkFont(size=12), text_color=MUTED, anchor="w",
            wraplength=300, justify="left",
        ).pack(fill="x", padx=12, pady=(0, 14))

        self.menu_panel = ctk.CTkFrame(
            self.columns, fg_color=WHITE, corner_radius=14,
            border_width=1, border_color=BORDER,
        )
        self.menu_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)

    def _compact(self, value):
        return "".join(ch.lower() for ch in value if ch.isalnum())

    def _find_image(self, name, size):
        assets_dir = Path(__file__).resolve().parent.parent / "assets"
        if not assets_dir.exists():
            return None
        files = [
            path for path in assets_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        ]
        target = self._compact(name)
        matches = [path for path in files if target and target in self._compact(path.stem)]
        if not matches:
            parts = [part for part in name.replace("ร้าน", "").split() if len(part) >= 3]
            matches = [
                path for path in files
                if any(self._compact(part) in self._compact(path.stem) for part in parts)
            ]
        if not matches:
            return None
        try:
            with Image.open(matches[0]) as source:
                picture = source.convert("RGB")
                return ctk.CTkImage(light_image=picture, dark_image=picture, size=size)
        except (OSError, ValueError):
            return None

    def toggle_favorite(self):
        # Visual toggle; persistent favorite storage can be connected when a favorites table exists.
        self.is_favorite = not self.is_favorite
        self.favorite_button.configure(
            text="♥" if self.is_favorite else "♡",
            text_color=ORANGE if self.is_favorite else ORANGE,
        )

    def _clear_menu_panel(self):
        for widget in self.menu_panel.winfo_children():
            widget.destroy()

    def show_menu_list(self):
        self._clear_menu_panel()
        ctk.CTkLabel(
            self.menu_panel, text="เมนูทั้งหมด",
            font=ctk.CTkFont(size=19, weight="bold"), text_color=TEXT, anchor="w",
        ).pack(fill="x", padx=14, pady=(14, 8))

        rows = ctk.CTkScrollableFrame(self.menu_panel, fg_color="transparent", corner_radius=0)
        rows.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        if self.shop_name in self.curry_shops:
            prices = self.curry_shops[self.shop_name]["prices"]
            dishes = self.curry_shops[self.shop_name]["dishes"]
            if not prices or not dishes:
                ctk.CTkLabel(
                    rows, text="วันนี้ยังไม่มีเมนูพร้อมขาย", text_color=MUTED,
                ).pack(pady=20)
                return
            self._make_menu_row(rows, "ข้าวราดแกง", min(prices.values()), curry=True)
        else:
            shop_menus = self.menus.get(self.shop_name, {})
            if not shop_menus:
                ctk.CTkLabel(
                    rows, text="วันนี้ยังไม่มีเมนูพร้อมขาย", text_color=MUTED,
                ).pack(pady=20)
            for menu_name, price in shop_menus.items():
                self._make_menu_row(rows, menu_name, price)

    def _make_menu_row(self, parent, menu_name, price, curry=False):
        row = ctk.CTkFrame(
            parent, fg_color=WHITE, corner_radius=10,
            border_width=1, border_color="#F0F0F0",
        )
        row.pack(fill="x", padx=3, pady=5)
        image = self._find_image(menu_name, (76, 66))
        image_area = ctk.CTkFrame(row, fg_color=SOFT_ORANGE, corner_radius=8, width=76, height=66)
        image_area.pack(side="left", padx=8, pady=8)
        image_area.pack_propagate(False)
        if image:
            image_label = ctk.CTkLabel(image_area, text="", image=image)
            image_label.pack(fill="both", expand=True)
            image_label.image = image
        else:
            ctk.CTkLabel(image_area, text="🍲", font=ctk.CTkFont(size=27), text_color=ORANGE).pack(expand=True)

        text_frame = ctk.CTkFrame(row, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=(2, 4), pady=8)
        ctk.CTkLabel(
            text_frame, text=menu_name, font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT, anchor="w", wraplength=210,
        ).pack(fill="x", pady=(5, 3))
        ctk.CTkLabel(
            text_frame, text=f"{price} บาท" if not curry else f"เริ่มต้น {price} บาท",
            font=ctk.CTkFont(size=13), text_color=MUTED, anchor="w",
        ).pack(fill="x")
        ctk.CTkButton(
            row, text="+ เพิ่ม", width=76, height=34, corner_radius=8,
            fg_color=ORANGE, hover_color=ORANGE_HOVER, text_color=WHITE,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=partial(self.show_menu_details, "ข้าวราดแกง" if curry else menu_name),
        ).pack(side="right", padx=9, pady=8)

    def show_menu_details(self, menu_name):
        self._clear_menu_panel()
        header = ctk.CTkFrame(self.menu_panel, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 6))
        ctk.CTkButton(
            header, text="← เมนูทั้งหมด", width=112, height=32, corner_radius=8,
            fg_color=WHITE, hover_color="#FFF0E9", text_color=TEXT,
            border_width=1, border_color=BORDER, command=self.show_menu_list,
        ).pack(side="left")
        ctk.CTkLabel(
            self.menu_panel, text=menu_name,
            font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT,
        ).pack(pady=5)

        self.details_area = ctk.CTkScrollableFrame(self.menu_panel, fg_color="transparent")
        self.details_area.pack(fill="both", expand=True, padx=12, pady=4)
        if self.shop_name in self.curry_shops:
            self.show_curry_options(self.details_area)
        else:
            self.show_regular_menu(self.details_area, menu_name)

        self.message_label = ctk.CTkLabel(self.menu_panel, text="", wraplength=360, text_color=ORANGE)
        self.message_label.pack(pady=(4, 10))

    def show_regular_menu(self, parent, menu_name):
        self.menu_choices = {}
        self.menu_price_labels = {}
        price = menu.calculate_price(self.shop_name, menu_name, menu_data=self.menu_data)
        ctk.CTkLabel(parent, text=f"ราคาเริ่มต้น {price} บาท", text_color=MUTED).pack(pady=6)
        self.menu_choices[menu_name] = {}
        for group_name, choices in self.shop_options.get(self.shop_name, {}).items():
            if not choices:
                continue
            ctk.CTkLabel(
                parent, text=group_name, font=ctk.CTkFont(size=13, weight="bold"),
                text_color=TEXT,
            ).pack(pady=(8, 2))
            first_choice = list(choices)[0]
            choice_variable = ctk.StringVar(value=first_choice)
            self.menu_choices[menu_name][group_name] = choice_variable
            for choice, extra_price in choices.items():
                choice_text = choice + (f" (+{extra_price} บาท)" if extra_price > 0 else "")
                ctk.CTkRadioButton(
                    parent, text=choice_text, variable=choice_variable, value=choice,
                    command=partial(self.update_regular_price, menu_name),
                    fg_color=ORANGE, hover_color=ORANGE_HOVER,
                ).pack(anchor="w", pady=3)
        self.menu_price_labels[menu_name] = ctk.CTkLabel(
            parent, text=f"ราคาต่อรายการ {price} บาท",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=ORANGE,
        )
        self.menu_price_labels[menu_name].pack(pady=10)
        note_entry = ctk.CTkEntry(
            parent, placeholder_text="หมายเหตุถึงร้าน (ไม่บังคับ)", height=36,
        )
        note_entry.pack(fill="x", pady=5)
        ctk.CTkButton(
            parent, text="เพิ่มลงตะกร้า", height=38, corner_radius=9,
            fg_color=ORANGE, hover_color=ORANGE_HOVER,
            command=partial(self.add_regular_item, menu_name, note_entry),
        ).pack(fill="x", pady=8)

    def get_selected_options(self, menu_name):
        return {
            group_name: choice_variable.get()
            for group_name, choice_variable in self.menu_choices[menu_name].items()
        }

    def update_regular_price(self, menu_name):
        selected_options = self.get_selected_options(menu_name)
        price = menu.calculate_price(
            self.shop_name, menu_name, selected_options=selected_options, menu_data=self.menu_data,
        )
        self.menu_price_labels[menu_name].configure(text=f"ราคาต่อรายการ {price} บาท")

    def add_regular_item(self, menu_name, note_entry):
        selected_options = self.get_selected_options(menu_name)
        price = menu.calculate_price(
            self.shop_name, menu_name, selected_options=selected_options, menu_data=self.menu_data,
        )
        options = [f"{group_name}: {choice}" for group_name, choice in selected_options.items()]
        self.add_to_cart(menu_name, price, options, note_entry.get())
        self.message_label.configure(text=f"เพิ่ม {menu_name} ลงตะกร้าแล้ว")

    def show_curry_options(self, parent):
        shop = self.curry_shops[self.shop_name]
        self.dish_count = ctk.IntVar(value=min(shop["prices"]))
        ctk.CTkLabel(parent, text="เลือกราคาและกับข้าว", text_color=TEXT).pack(pady=(6, 4))
        for count, price in shop["prices"].items():
            ctk.CTkRadioButton(
                parent, text=f"ราด {count} อย่าง — {price} บาท",
                variable=self.dish_count, value=count, command=self.update_price,
                fg_color=ORANGE, hover_color=ORANGE_HOVER,
            ).pack(anchor="w", pady=3)

        ctk.CTkLabel(parent, text="เลือกกับข้าวให้ครบตามจำนวนที่กำหนด", text_color=TEXT).pack(pady=(10, 4))
        self.dish_choices = {}
        for dish in shop["dishes"]:
            choice = ctk.BooleanVar(value=False)
            self.dish_choices[dish] = choice
            ctk.CTkCheckBox(
                parent, text=dish, variable=choice, fg_color=ORANGE, hover_color=ORANGE_HOVER,
            ).pack(anchor="w", pady=3)

        self.extra_rice = ctk.BooleanVar(value=False)
        rice_text = "เพิ่มข้าว"
        if shop["extra_rice_price"] > 0:
            rice_text += f" (+{shop['extra_rice_price']} บาท)"
        ctk.CTkCheckBox(
            parent, text=rice_text, variable=self.extra_rice, command=self.update_price,
            state="normal" if shop.get("extra_rice_available") else "disabled",
            fg_color=ORANGE, hover_color=ORANGE_HOVER,
        ).pack(anchor="w", pady=8)
        self.note_entry = ctk.CTkEntry(parent, placeholder_text="หมายเหตุ เช่น แยกน้ำแกง", height=36)
        self.note_entry.pack(fill="x", pady=6)
        self.price_label = ctk.CTkLabel(
            parent, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color=ORANGE,
        )
        self.price_label.pack(pady=8)
        self.update_price()
        ctk.CTkButton(
            parent, text="เพิ่มลงตะกร้า", height=38, corner_radius=9,
            fg_color=ORANGE, hover_color=ORANGE_HOVER, command=self.add_curry_item,
        ).pack(fill="x", pady=8)

    def update_price(self):
        price = menu.calculate_price(
            self.shop_name, "ข้าวราดแกง", self.dish_count.get(), self.extra_rice.get(),
            menu_data=self.menu_data,
        )
        self.price_label.configure(text=f"ราคาต่อจาน {price} บาท")

    def add_curry_item(self):
        selected_dishes = [dish for dish, choice in self.dish_choices.items() if choice.get()]
        count = self.dish_count.get()
        error = menu.check_selection(self.shop_name, count, selected_dishes, self.menu_data)
        if error:
            self.message_label.configure(text=error)
            return
        price = menu.calculate_price(
            self.shop_name, "ข้าวราดแกง", count, self.extra_rice.get(), menu_data=self.menu_data,
        )
        options = selected_dishes.copy()
        if self.extra_rice.get():
            options.append("เพิ่มข้าว")
        self.add_to_cart(f"ข้าวราดแกง {count} อย่าง", price, options, self.note_entry.get())
        self.message_label.configure(text="เพิ่มข้าวราดแกงลงตะกร้าแล้ว")
