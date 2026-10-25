from functools import partial
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from Backend import cart, catalog, users
from Frontend.login_page import LoginPage
from Frontend.menu_page import MenuPage
from Frontend.checkout_page import CheckoutPage
from Frontend.shop_orders_page import ShopOrdersPage
from Frontend.order_history_page import OrderHistoryPage


class CanteenApp(ctk.CTk):
    """Main window for the KMITL Canteen desktop application."""

    def __init__(self):
        super().__init__()
        self.title("KMITL Canteen")
        self.geometry("1200x760")
        self.minsize(900, 600)
        self.configure(fg_color="#F7F7F7")

        self.canteens = {}
        self.cart = []
        self.current_user = None
        self.last_page = self.show_canteens

        # Header
        self.header = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, height=72)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        brand = ctk.CTkFrame(self.header, fg_color="transparent")
        brand.pack(side="left", padx=24, pady=12)
        ctk.CTkLabel(brand, text="KMITL", text_color="#F45B2A",
                     font=ctk.CTkFont(size=25, weight="bold")).pack(side="left")
        ctk.CTkLabel(brand, text=" Canteen", text_color="#242424",
                     font=ctk.CTkFont(size=23, weight="bold")).pack(side="left")
        self.search_entry = ctk.CTkEntry(
            self.header, placeholder_text="⌕  ค้นหาร้านหรือเมนู...", width=270,
            height=38, corner_radius=18, border_color="#E7E7E7", fg_color="#FFFFFF",
        )
        self.search_entry.pack(side="right", padx=(8, 24), pady=16)
        self.profile_label = ctk.CTkLabel(self.header, text="👤", font=ctk.CTkFont(size=22))
        self.profile_label.pack(side="right", padx=12)

        # Body: left navigation and page content
        self.body = ctk.CTkFrame(self, fg_color="#F7F7F7", corner_radius=0)
        self.body.pack(fill="both", expand=True)
        self.sidebar = ctk.CTkFrame(self.body, width=205, fg_color="#FFFFFF", corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=(0, 12))
        self.sidebar.pack_propagate(False)
        self.nav_buttons = {}
        nav_items = [
            ("โรงอาหาร", self.show_canteens, "⌂"),
            ("ร้านค้า", self.show_all_shops, "▣"),
        ]
        for label, command, symbol in nav_items:
            button = ctk.CTkButton(
                self.sidebar, text=f"{symbol}   {label}", command=command,
                height=42, corner_radius=10, anchor="w", fg_color="transparent",
                hover_color="#FFF0E9", text_color="#333333",
                font=ctk.CTkFont(size=14),
            )
            button.pack(fill="x", padx=12, pady=5)
            self.nav_buttons[label] = button
        ctk.CTkFrame(self.sidebar, fg_color="transparent", height=12).pack()
        self.cart_button = ctk.CTkButton(
            self.sidebar, text="🛒   ตะกร้า (0 ชิ้น)", command=self.show_cart,
            height=42, corner_radius=10, anchor="w", fg_color="transparent",
            hover_color="#FFF0E9", text_color="#333333",
        )
        self.history_button = ctk.CTkButton(
            self.sidebar, text="◷   คำสั่งซื้อของฉัน", command=self.show_order_history,
            height=42, corner_radius=10, anchor="w", fg_color="transparent",
            hover_color="#FFF0E9", text_color="#333333",
        )
        self.favorites_button = ctk.CTkButton(
            self.sidebar, text="♡   เมนูโปรด", command=self.show_favorites,
            height=42, corner_radius=10, anchor="w", fg_color="transparent",
            hover_color="#FFF0E9", text_color="#333333",
        )
        self.nav_buttons["ตะกร้า"] = self.cart_button
        self.nav_buttons["คำสั่งซื้อของฉัน"] = self.history_button
        self.nav_buttons["เมนูโปรด"] = self.favorites_button
        self.shop_button = ctk.CTkButton(
            self.sidebar, text="▣   ออเดอร์ของร้าน", command=self.show_shop_orders,
            height=42, corner_radius=10, anchor="w", fg_color="transparent",
            hover_color="#FFF0E9", text_color="#333333",
        )
        self.logout_button = ctk.CTkButton(
            self.sidebar, text="ออกจากระบบ", command=self.show_login,
            height=38, corner_radius=10, fg_color="#F45B2A", hover_color="#DF4B20",
        )

        self.content = ctk.CTkFrame(self.body, fg_color="#F7F7F7", corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True, padx=(8, 22), pady=18)
        self.page_title_label = ctk.CTkLabel(
            self.content, text="", font=ctk.CTkFont(size=25, weight="bold"),
            text_color="#242424", anchor="w",
        )
        self.page_title_label.pack(fill="x", padx=12, pady=(8, 14))
        self.page_frame = ctk.CTkScrollableFrame(
            self.content, fg_color="transparent", corner_radius=0,
        )
        self.page_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.show_login()

    def show_login(self):
        users.logout()
        self.current_user = None
        self.cart.clear()
        self.last_page = self.show_canteens
        self.update_cart_button()
        self.sidebar.pack_forget()
        self.clear_page()
        self.page_title_label.configure(text="ยินดีต้อนรับ")
        self.profile_label.configure(text="👤")
        LoginPage(self.page_frame, self.login_finished).pack(fill="x", padx=12, pady=12)

    def login_finished(self, user):
        self.current_user = user
        self.profile_label.configure(text=f"👤  {user['display_name']}")
        self.sidebar.pack(side="left", fill="y", padx=(0, 12))
        if user['role'] == 'shop':
            self.cart_button.pack_forget()
            self.history_button.pack_forget()
            self.favorites_button.pack_forget()
            self.shop_button.pack(fill="x", padx=12, pady=5)
            self.logout_button.pack(side="bottom", fill="x", padx=12, pady=16)
            self.show_shop_orders()
        else:
            self.shop_button.pack_forget()
            self.cart_button.pack(fill="x", padx=12, pady=5)
            self.favorites_button.pack(fill="x", padx=12, pady=5)
            self.history_button.pack(fill="x", padx=12, pady=5)
            self.logout_button.pack(side="bottom", fill="x", padx=12, pady=16)
            self.show_canteens()

    def clear_page(self):
        # ลบเนื้อหาหน้าเดิม ก่อนแสดงหน้าใหม่
        for widget in self.page_frame.winfo_children():
            widget.destroy()

    def show_canteens(self):
        users.require_user('customer')
        self._set_active_nav("โรงอาหาร")
        self.canteens = catalog.get_canteens()
        self.last_page = self.show_canteens
        self.clear_page()
        self.page_title_label.configure(text="เลือกโรงอาหาร")

        intro = ctk.CTkLabel(
            self.page_frame, text="ค้นหาร้านอาหารอร่อย ๆ ภายใน สจล.",
            text_color="#777777", font=ctk.CTkFont(size=14), anchor="w",
        )
        intro.pack(fill="x", padx=8, pady=(0, 16))

        grid = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        grid.pack(fill="x", padx=4, pady=4)
        columns = 3
        for column in range(columns):
            grid.grid_columnconfigure(column, weight=1, uniform="canteen_cards")

        if not self.canteens:
            ctk.CTkLabel(
                grid, text="ยังไม่มีข้อมูลโรงอาหารในฐานข้อมูล",
                text_color="#777777", font=ctk.CTkFont(size=15),
            ).grid(row=0, column=0, padx=8, pady=8, sticky="w")
            return

        for index, (canteen_name, shops) in enumerate(self.canteens.items()):
            row, column = divmod(index, columns)
            card = ctk.CTkFrame(
                grid, fg_color="#FFFFFF", corner_radius=15,
                border_width=1, border_color="#ECECEC",
            )
            card.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
            banner = ctk.CTkFrame(card, fg_color="#FBE6D9", corner_radius=11, height=112)
            banner.pack(fill="x", padx=8, pady=(8, 4))
            banner.pack_propagate(False)
            ctk.CTkLabel(
                banner, text="🏫", font=ctk.CTkFont(size=42), text_color="#F45B2A",
            ).pack(expand=True)
            ctk.CTkLabel(
                card, text=canteen_name, font=ctk.CTkFont(size=17, weight="bold"),
                text_color="#242424", anchor="w", wraplength=220,
            ).pack(fill="x", padx=12, pady=(8, 3))
            ctk.CTkLabel(
                card, text=f"{len(shops)} ร้านอาหาร", font=ctk.CTkFont(size=12),
                text_color="#777777", anchor="w",
            ).pack(fill="x", padx=12, pady=(0, 10))
            ctk.CTkButton(
                card, text="ดูร้านค้า", height=36, corner_radius=9,
                fg_color="#F45B2A", hover_color="#DF4B20",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=partial(self.show_shops, canteen_name),
            ).pack(fill="x", padx=12, pady=(0, 12))

    def _set_active_nav(self, active_label):
        """Highlight the current customer navigation item in the left sidebar."""
        for label, button in self.nav_buttons.items():
            active = label == active_label
            button.configure(
                fg_color="#F45B2A" if active else "transparent",
                hover_color="#DF4B20" if active else "#FFF0E9",
                text_color="#FFFFFF" if active else "#333333",
            )

    def _shop_image(self, shop_name, size=(220, 100)):
        """Load a shop photo from assets when a matching image exists."""
        assets_dir = Path(__file__).resolve().parent.parent / "assets"
        if not assets_dir.exists():
            return None

        # Only use a file whose name matches this shop, to avoid showing unrelated assets
        # such as payment QR codes as food/shop photos.
        def compact(value):
            return "".join(ch.lower() for ch in value if ch.isalnum())

        target = compact(shop_name)
        image_files = [
            path for path in assets_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        ]
        matches = [path for path in image_files if target and target in compact(path.stem)]
        if not matches:
            # Also support filenames that contain a distinctive part of a longer Thai shop name.
            shop_parts = [part for part in shop_name.replace("ร้าน", "").split() if len(part) >= 3]
            matches = [
                path for path in image_files
                if any(compact(part) in compact(path.stem) for part in shop_parts)
            ]
        if not matches:
            return None
        try:
            with Image.open(matches[0]) as source:
                picture = source.convert("RGB")
                return ctk.CTkImage(light_image=picture, dark_image=picture, size=size)
        except (OSError, ValueError):
            return None

    def _make_shop_card(self, parent, canteen_name, shop_name, row, column, columns=3):
        card = ctk.CTkFrame(
            parent, fg_color="#FFFFFF", corner_radius=14,
            border_width=1, border_color="#EAEAEA",
        )
        card.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        image = self._shop_image(shop_name)
        image_area = ctk.CTkFrame(
            card, fg_color="#FBE6D9", corner_radius=10, height=105,
        )
        image_area.pack(fill="x", padx=8, pady=(8, 4))
        image_area.pack_propagate(False)
        if image:
            image_label = ctk.CTkLabel(image_area, text="", image=image)
            image_label.pack(fill="both", expand=True)
            # Keep a reference so CustomTkinter doesn't release the image.
            image_label.image = image
        else:
            ctk.CTkLabel(
                image_area, text="🍜", font=ctk.CTkFont(size=42),
                text_color="#F45B2A",
            ).pack(expand=True)

        ctk.CTkLabel(
            card, text=shop_name, font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#242424", anchor="w", wraplength=190,
        ).pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(
            card, text=canteen_name, font=ctk.CTkFont(size=12),
            text_color="#777777", anchor="w",
        ).pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(
            card, text="ดูเมนู  →", height=34, corner_radius=9,
            fg_color="#F45B2A", hover_color="#DF4B20",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=partial(self.show_menu, canteen_name, shop_name),
        ).pack(fill="x", padx=10, pady=(0, 10))

    def show_shops(self, canteen_name):
        """Show shops in the selected canteen as a three-column card grid."""
        users.require_user('customer')
        self.canteens = catalog.get_canteens()
        self.last_page = partial(self.show_shops, canteen_name)
        self._set_active_nav("โรงอาหาร")
        self.clear_page()
        self.page_title_label.configure(text=canteen_name)

        title_row = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        title_row.pack(fill="x", padx=8, pady=(0, 10))
        ctk.CTkButton(
            title_row, text="←", width=42, height=36, corner_radius=9,
            fg_color="#FFFFFF", hover_color="#FFF0E9", text_color="#333333",
            border_width=1, border_color="#EAEAEA", command=self.show_canteens,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            title_row, text=f"ร้านค้าใน{canteen_name}",
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#242424",
        ).pack(side="left")

        shops = self.canteens.get(canteen_name, [])
        if not shops:
            ctk.CTkLabel(
                self.page_frame, text="ยังไม่มีร้านค้าในโรงอาหารนี้",
                text_color="#777777",
            ).pack(pady=16)
            return

        grid = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=2, pady=2)
        columns = 3
        for col in range(columns):
            grid.grid_columnconfigure(col, weight=1, uniform="shop_cards")
        for index, shop_name in enumerate(shops):
            row, column = divmod(index, columns)
            self._make_shop_card(grid, canteen_name, shop_name, row, column, columns)

    def show_all_shops(self):
        """Show every shop from every canteen in a card grid grouped by canteen."""
        users.require_user('customer')
        self.canteens = catalog.get_canteens()
        self.last_page = self.show_all_shops
        self._set_active_nav("ร้านค้า")
        self.clear_page()
        self.page_title_label.configure(text="ร้านค้าทั้งหมด")

        if not self.canteens or not any(self.canteens.values()):
            ctk.CTkLabel(
                self.page_frame, text="ยังไม่มีข้อมูลร้านค้าในฐานข้อมูล",
                text_color="#777777", font=ctk.CTkFont(size=15),
            ).pack(pady=20)
            return

        for canteen_name, shop_names in self.canteens.items():
            if not shop_names:
                continue
            section = ctk.CTkFrame(
                self.page_frame, fg_color="transparent", corner_radius=0,
            )
            section.pack(fill="x", padx=2, pady=(2, 12))
            ctk.CTkLabel(
                section, text=canteen_name,
                font=ctk.CTkFont(size=19, weight="bold"),
                text_color="#242424", anchor="w",
            ).pack(fill="x", padx=8, pady=(8, 4))
            grid = ctk.CTkFrame(section, fg_color="transparent")
            grid.pack(fill="x")
            columns = 3
            for col in range(columns):
                grid.grid_columnconfigure(col, weight=1, uniform=f"shops_{canteen_name}")
            for index, shop_name in enumerate(shop_names):
                row, column = divmod(index, columns)
                self._make_shop_card(grid, canteen_name, shop_name, row, column, columns)

    def show_menu(self, canteen_name, shop_name):
        self.last_page = partial(self.show_menu, canteen_name, shop_name)
        self._set_active_nav("ร้านค้า")
        self.clear_page()
        # The redesigned MenuPage contains its own shop title and back button.
        self.page_title_label.configure(text="")

        menu_page = MenuPage(
            self.page_frame,
            canteen_name,
            shop_name,
            partial(self.add_to_cart, canteen_name, shop_name),
            partial(self.show_shops, canteen_name),
        )
        menu_page.pack(fill="x")

    def add_to_cart(self, canteen_name, shop_name, menu_name, price, options, note):
        cart.add_item(self.cart, canteen_name, shop_name, menu_name, price, options, note)
        self.update_cart_button()

    def update_cart_button(self):
        quantity = cart.get_total_quantity(self.cart)
        self.cart_button.configure(text=f"ตะกร้า ({quantity} ชิ้น)")

    def _menu_image(self, menu_name, size=(76, 62)):
        """Load a food image from assets when its filename matches the menu name."""
        assets_dir = Path(__file__).resolve().parent.parent / "assets"
        if not assets_dir.exists():
            return None

        def compact(value):
            return "".join(ch.lower() for ch in value if ch.isalnum())

        target = compact(menu_name)
        image_files = [
            path for path in assets_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        ]
        matches = [path for path in image_files if target and target in compact(path.stem)]
        if not matches:
            parts = [part for part in menu_name.split() if len(part) >= 3]
            matches = [
                path for path in image_files
                if any(compact(part) in compact(path.stem) for part in parts)
            ]
        if not matches:
            return None
        try:
            with Image.open(matches[0]) as source_image:
                picture = source_image.convert("RGB")
                return ctk.CTkImage(light_image=picture, dark_image=picture, size=size)
        except (OSError, ValueError):
            return None

    def increase_quantity(self, item):
        cart.increase_quantity(item)
        self.show_cart()

    def decrease_quantity(self, item):
        cart.decrease_quantity(item)
        self.show_cart()

    def remove_item(self, item):
        cart.remove_item(self.cart, item)
        self.show_cart()

    def clear_cart(self):
        if not self.cart:
            return
        confirmed = messagebox.askyesno(
            "ล้างตะกร้า", "ต้องการลบอาหารทั้งหมดออกจากตะกร้าหรือไม่?", parent=self
        )
        if confirmed:
            self.cart.clear()
            self.update_cart_button()
            self.show_cart()

    def show_cart(self):
        """Display cart items in a compact, horizontal layout matching the reference."""
        users.require_user('customer')
        self._set_active_nav("ตะกร้า")
        self.clear_page()
        self.update_cart_button()
        self.page_title_label.configure(text="ตะกร้าของฉัน")

        heading = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        heading.pack(fill="x", padx=8, pady=(0, 8))
        ctk.CTkLabel(
            heading, text="ตะกร้าของฉัน", font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#242424", anchor="w",
        ).pack(side="left")
        ctk.CTkButton(
            heading, text="▤  ล้างตะกร้า", width=112, height=30, corner_radius=8,
            fg_color="transparent", hover_color="#FFF0E9", text_color="#F45B2A",
            command=self.clear_cart,
        ).pack(side="right")

        if not self.cart:
            empty = ctk.CTkFrame(self.page_frame, fg_color="#FFFFFF", corner_radius=12)
            empty.pack(fill="x", padx=8, pady=8)
            ctk.CTkLabel(
                empty, text="ตะกร้ายังว่างอยู่", font=ctk.CTkFont(size=16),
                text_color="#777777",
            ).pack(pady=28)
            ctk.CTkButton(
                self.page_frame, text="เลือกอาหาร", height=42, corner_radius=9,
                fg_color="#F45B2A", hover_color="#DF4B20",
                command=self.show_all_shops,
            ).pack(fill="x", padx=8, pady=8)
            return

        items_area = ctk.CTkFrame(self.page_frame, fg_color="#FFFFFF", corner_radius=12)
        items_area.pack(fill="x", padx=8, pady=(0, 8))
        for index, item in enumerate(list(self.cart)):
            row = ctk.CTkFrame(items_area, fg_color="transparent", corner_radius=8)
            row.pack(fill="x", padx=10, pady=6)
            row.grid_columnconfigure(1, weight=1)

            image = self._menu_image(item["menu"])
            image_box = ctk.CTkFrame(row, fg_color="#FBE6D9", corner_radius=8, width=76, height=62)
            image_box.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="w")
            image_box.grid_propagate(False)
            if image:
                image_label = ctk.CTkLabel(image_box, text="", image=image)
                image_label.pack(fill="both", expand=True)
                image_label.image = image
            else:
                ctk.CTkLabel(
                    image_box, text="🍜", font=ctk.CTkFont(size=27), text_color="#F45B2A",
                ).pack(expand=True)

            details = ctk.CTkFrame(row, fg_color="transparent")
            details.grid(row=0, column=1, rowspan=2, sticky="nsew")
            ctk.CTkLabel(
                details, text=item["menu"], font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#242424", anchor="w",
            ).pack(fill="x", pady=(3, 0))
            ctk.CTkLabel(
                details, text=f"{item['price']} บาท", font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#F45B2A", anchor="w",
            ).pack(fill="x")
            if item.get("options"):
                ctk.CTkLabel(
                    details, text=", ".join(item["options"]), font=ctk.CTkFont(size=10),
                    text_color="#777777", anchor="w", wraplength=260,
                ).pack(fill="x")
            if item.get("note"):
                ctk.CTkLabel(
                    details, text=f"หมายเหตุ: {item['note']}", font=ctk.CTkFont(size=10),
                    text_color="#777777", anchor="w", wraplength=260,
                ).pack(fill="x")

            controls = ctk.CTkFrame(row, fg_color="transparent")
            controls.grid(row=0, column=2, rowspan=2, padx=(8, 2), sticky="e")
            ctk.CTkButton(
                controls, text="−", width=28, height=30, corner_radius=6,
                fg_color="#F5F5F5", hover_color="#EAEAEA", text_color="#333333",
                command=partial(self.decrease_quantity, item),
                state="disabled" if item["quantity"] <= 1 else "normal",
            ).pack(side="left", padx=1)
            ctk.CTkLabel(
                controls, text=str(item["quantity"]), width=28,
                font=ctk.CTkFont(size=13, weight="bold"), text_color="#242424",
            ).pack(side="left", padx=1)
            ctk.CTkButton(
                controls, text="+", width=28, height=30, corner_radius=6,
                fg_color="#F5F5F5", hover_color="#EAEAEA", text_color="#F45B2A",
                command=partial(self.increase_quantity, item),
            ).pack(side="left", padx=1)
            ctk.CTkButton(
                controls, text="♜", width=28, height=30, corner_radius=6,
                fg_color="transparent", hover_color="#FFF0E9", text_color="#777777",
                command=partial(self.remove_item, item),
            ).pack(side="left", padx=(8, 0))

            if index < len(self.cart) - 1:
                ctk.CTkFrame(items_area, height=1, fg_color="#EEEEEE").pack(fill="x", padx=10)

        total = sum(cart.get_item_total(item) for item in self.cart)
        summary = ctk.CTkFrame(self.page_frame, fg_color="transparent")
        summary.pack(fill="x", padx=8, pady=(4, 2))
        ctk.CTkLabel(
            summary, text="รวมทั้งหมด", font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#242424",
        ).pack(side="left")
        ctk.CTkLabel(
            summary, text=f"{total} บาท", font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#242424",
        ).pack(side="right")

        shops = cart.get_shops(self.cart)
        if len(shops) == 1:
            canteen_name, shop_name = shops[0]
            ctk.CTkButton(
                self.page_frame, text="สั่งอาหาร", height=42, corner_radius=9,
                fg_color="#F45B2A", hover_color="#DF4B20",
                font=ctk.CTkFont(size=14, weight="bold"),
                command=partial(self.show_checkout, canteen_name, shop_name),
            ).pack(fill="x", padx=8, pady=(8, 12))
        else:
            ctk.CTkLabel(
                self.page_frame,
                text="มีอาหารจากหลายร้าน กรุณาสั่งแยกตามร้าน",
                font=ctk.CTkFont(size=12), text_color="#777777",
            ).pack(anchor="w", padx=8, pady=(8, 4))
            for canteen_name, shop_name in shops:
                shop_items = cart.get_shop_items(self.cart, canteen_name, shop_name)
                shop_total = cart.get_total_price(shop_items)
                ctk.CTkButton(
                    self.page_frame,
                    text=f"สั่งอาหาร — {shop_name} ({shop_total} บาท)",
                    height=38, corner_radius=9, fg_color="#F45B2A", hover_color="#DF4B20",
                    command=partial(self.show_checkout, canteen_name, shop_name),
                ).pack(fill="x", padx=8, pady=4)

    def show_shop_cart(self, canteen_name, shop_name):
        # Keep older navigation callbacks working; the cart page now shows all items.
        self.show_cart()

    def show_checkout(self, canteen_name, shop_name):
        users.require_user('customer')
        shop_items = cart.get_shop_items(self.cart, canteen_name, shop_name)
        if not shop_items:
            self.show_shop_cart(canteen_name, shop_name)
            return
        self.clear_page()
        self.page_title_label.configure(text="ข้อมูลรับอาหารและตรวจรายการ")
        page = CheckoutPage(
            self.page_frame, canteen_name, shop_name, shop_items,
            partial(self.show_shop_cart, canteen_name, shop_name),
            partial(self.order_saved, canteen_name, shop_name),
        )
        page.pack(fill="x")

    def order_saved(self, canteen_name, shop_name, order_id):
        ordered_items = cart.get_shop_items(self.cart, canteen_name, shop_name)
        for item in ordered_items:
            cart.remove_item(self.cart, item)
        self.update_cart_button()
        self.clear_page()
        self.page_title_label.configure(text="รอตรวจสอบการชำระเงิน")

        card = ctk.CTkFrame(
            self.page_frame, fg_color="#FFFFFF", corner_radius=18,
            border_width=1, border_color="#EAEAEA",
        )
        card.pack(fill="x", padx=18, pady=18)
        ctk.CTkLabel(
            card, text="✓", font=ctk.CTkFont(size=42, weight="bold"),
            text_color="#F45B2A",
        ).pack(pady=(24, 4))
        ctk.CTkLabel(
            card, text="ส่งคำสั่งซื้อเรียบร้อยแล้ว",
            font=ctk.CTkFont(size=23, weight="bold"), text_color="#242424",
        ).pack(pady=5)
        ctk.CTkLabel(
            card, text=f"เลขคำสั่งซื้อ  #{order_id}",
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#F45B2A",
        ).pack(pady=5)
        ctk.CTkLabel(
            card, text=f"{canteen_name} / {shop_name}",
            font=ctk.CTkFont(size=16), text_color="#333333",
        ).pack(pady=4)
        ctk.CTkLabel(
            card,
            text="รับแจ้งชำระแล้ว รอตรวจสอบเงินเข้า\nยังไม่ยืนยันการชำระเงินหรือส่งให้ร้านทำอาหาร",
            font=ctk.CTkFont(size=15), text_color="#777777", justify="center",
        ).pack(pady=(8, 18))
        ctk.CTkButton(
            card, text="ติดตามคำสั่งซื้อนี้",
            command=partial(self.show_order_history, order_id),
            width=280, height=42, corner_radius=10,
            fg_color="#F45B2A", hover_color="#DF4B20",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(pady=6)
        ctk.CTkButton(
            card, text="กลับไปดูตะกร้า", command=self.show_cart,
            width=280, height=38, corner_radius=10,
            fg_color="#F2F2F2", hover_color="#E7E7E7", text_color="#333333",
            font=ctk.CTkFont(size=14),
        ).pack(pady=(4, 22))

    def show_favorites(self):
        """Display the customer's favorites page."""
        users.require_user('customer')
        self._set_active_nav("เมนูโปรด")
        self.last_page = self.show_favorites
        self.clear_page()
        self.page_title_label.configure(text="♡  เมนูโปรด")
        ctk.CTkLabel(
            self.page_frame,
            text="เมนูโปรดของคุณจะแสดงที่นี่",
            text_color="#777777",
            font=ctk.CTkFont(size=15),
        ).pack(pady=24)

    def show_shop_orders(self):
        users.require_user('shop')
        self.clear_page()
        self.page_title_label.configure(text="จัดการออเดอร์ร้านค้า")
        page = ShopOrdersPage(self.page_frame, self.show_login)
        page.pack(fill="x")

    def show_order_history(self, order_id=None):
        users.require_user('customer')
        self._set_active_nav("คำสั่งซื้อของฉัน")
        self.clear_page()
        self.page_title_label.configure(text="คำสั่งซื้อและสถานะ")
        page = OrderHistoryPage(self.page_frame, self.show_canteens, order_id)
        page.pack(fill="x")
