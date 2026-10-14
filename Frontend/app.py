from functools import partial

import customtkinter as ctk

from Backend import cart, catalog
from Frontend.menu_page import MenuPage
from Frontend.checkout_page import CheckoutPage
from Frontend.shop_orders_page import ShopOrdersPage


class CanteenApp(ctk.CTk):
    """Main window for the KMITL Canteen desktop application."""

    def __init__(self):
        super().__init__()

        self.title("KMITL Canteen")
        self.geometry("1000x650")
        self.minsize(800, 500)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=24, pady=24)

        self.app_name_label = ctk.CTkLabel(
            self.main_frame,
            text="KMITL Canteen",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        self.app_name_label.pack(pady=(48, 12))

        self.canteens = catalog.get_canteens()

        self.page_title_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=18),
        )
        self.page_title_label.pack(pady=(0, 12))

        # ตะกร้าเก็บอยู่ในหน่วยความจำ ปิดแอปแล้วข้อมูลจะหาย
        self.cart = []
        self.last_page = self.show_canteens
        self.cart_button = ctk.CTkButton(
            self.main_frame,
            text="ตะกร้า (0 ชิ้น)",
            command=self.show_cart,
        )
        self.cart_button.pack(pady=4)
        self.shop_button = ctk.CTkButton(
            self.main_frame, text="ฝั่งร้านค้า (สาธิต)", command=self.show_shop_orders,
        )
        self.shop_button.pack(pady=4)

        self.page_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.page_frame.pack(fill="both", expand=True, padx=24, pady=12)

        self.show_canteens()

    def clear_page(self):
        # ลบเนื้อหาหน้าเดิม ก่อนแสดงหน้าใหม่
        for widget in self.page_frame.winfo_children():
            widget.destroy()

    def show_canteens(self):
        self.canteens = catalog.get_canteens()
        self.last_page = self.show_canteens
        self.clear_page()
        self.page_title_label.configure(text="เลือกโรงอาหาร")

        for canteen_name in self.canteens:
            canteen_button = ctk.CTkButton(
                self.page_frame,
                text=canteen_name,
                width=300,
                height=48,
                font=ctk.CTkFont(size=18),
                # จำชื่อโรงอาหารไว้ แล้วส่งให้ show_shops เมื่อกดปุ่ม
                command=partial(self.show_shops, canteen_name),
            )
            canteen_button.pack(pady=8)

    def show_shops(self, canteen_name):
        self.last_page = partial(self.show_shops, canteen_name)
        self.clear_page()
        self.page_title_label.configure(text=f"ร้านอาหาร — {canteen_name}")

        sample_label = ctk.CTkLabel(
            self.page_frame,
            text="ร้านตัวอย่าง — กดเลือกร้านเพื่อดูเมนู",
        )
        sample_label.pack(pady=(0, 12))

        for shop_name in self.canteens[canteen_name]:
            shop_button = ctk.CTkButton(
                self.page_frame,
                text=shop_name,
                width=300,
                height=40,
                font=ctk.CTkFont(size=18),
                command=partial(self.show_menu, canteen_name, shop_name),
            )
            shop_button.pack(pady=8)


        back_button = ctk.CTkButton(
            self.page_frame,
            text="กลับไปเลือกโรงอาหาร",
            command=self.show_canteens,
        )
        back_button.pack(pady=(24, 0))

    def show_menu(self, canteen_name, shop_name):
        self.last_page = partial(self.show_menu, canteen_name, shop_name)
        self.clear_page()
        self.page_title_label.configure(text=f"{canteen_name} — {shop_name}")

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

    def increase_quantity(self, item):
        cart.increase_quantity(item)
        self.show_shop_cart(item["canteen"], item["shop"])

    def decrease_quantity(self, item):
        cart.decrease_quantity(item)
        self.show_shop_cart(item["canteen"], item["shop"])

    def remove_item(self, item):
        cart.remove_item(self.cart, item)
        self.show_shop_cart(item["canteen"], item["shop"])

    def show_cart(self):
        self.clear_page()
        self.update_cart_button()
        self.page_title_label.configure(text="ตะกร้าของฉัน — เลือกร้าน")

        if not self.cart:
            empty_label = ctk.CTkLabel(self.page_frame, text="ยังไม่มีอาหารในตะกร้า")
            empty_label.pack(pady=12)

        for canteen_name, shop_name in cart.get_shops(self.cart):
            shop_items = cart.get_shop_items(self.cart, canteen_name, shop_name)
            quantity = cart.get_total_quantity(shop_items)
            total = cart.get_total_price(shop_items)
            shop_button = ctk.CTkButton(
                self.page_frame,
                text=f"{canteen_name} / {shop_name}\n{quantity} ชิ้น — {total} บาท",
                height=64,
                command=partial(self.show_shop_cart, canteen_name, shop_name),
            )
            shop_button.pack(fill="x", pady=8)

        ctk.CTkButton(
            self.page_frame, text="กลับไปเลือกอาหารต่อ", command=self.last_page,
        ).pack(pady=12)

    def show_shop_cart(self, canteen_name, shop_name):
        self.clear_page()
        self.update_cart_button()
        self.page_title_label.configure(text=f"ตะกร้า: {canteen_name} / {shop_name}")
        shop_items = cart.get_shop_items(self.cart, canteen_name, shop_name)
        if not shop_items:
            ctk.CTkLabel(self.page_frame, text="ตะกร้าร้านนี้ว่างแล้ว").pack(pady=12)

        total = cart.get_total_price(shop_items)
        for item in shop_items:
            item_total = cart.get_item_total(item)
            item_frame = ctk.CTkFrame(self.page_frame)
            item_frame.pack(fill="x", pady=8)
            item_label = ctk.CTkLabel(
                item_frame,
                text=(f"{item['canteen']} / {item['shop']}\n"
                      f"{item['menu']} — {item['price']} บาท × {item['quantity']} ชิ้น"
                      f" = {item_total} บาท"),
                font=ctk.CTkFont(size=18),
            )
            item_label.pack(pady=10)

            if item["options"]:
                options_label = ctk.CTkLabel(
                    item_frame, text="ตัวเลือก: " + ", ".join(item["options"]), wraplength=500,
                )
                options_label.pack(pady=4)
            if item["note"]:
                note_label = ctk.CTkLabel(
                    item_frame, text="หมายเหตุ: " + item["note"], wraplength=500,
                )
                note_label.pack(pady=4)

            button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            button_frame.pack(pady=(0, 12))

            decrease_button = ctk.CTkButton(
                button_frame,
                text="−",
                width=40,
                command=partial(self.decrease_quantity, item),
            )
            decrease_button.pack(side="left", padx=4)
            if item["quantity"] == 1:
                decrease_button.configure(state="disabled")

            quantity_label = ctk.CTkLabel(
                button_frame, text=str(item["quantity"]), width=40,
            )
            quantity_label.pack(side="left", padx=4)

            increase_button = ctk.CTkButton(
                button_frame,
                text="+",
                width=40,
                command=partial(self.increase_quantity, item),
            )
            increase_button.pack(side="left", padx=4)

            remove_button = ctk.CTkButton(
                button_frame,
                text="ลบรายการ",
                width=100,
                command=partial(self.remove_item, item),
            )
            remove_button.pack(side="left", padx=(16, 4))

        total_label = ctk.CTkLabel(
            self.page_frame,
            text=f"รวมร้านนี้ {total} บาท",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        total_label.pack(pady=12)

        if shop_items:
            ctk.CTkButton(
                self.page_frame, text="สั่งอาหารร้านนี้",
                command=partial(self.show_checkout, canteen_name, shop_name),
            ).pack(pady=8)

        back_button = ctk.CTkButton(
            self.page_frame,
            text="เพิ่มอาหารจากร้านนี้",
            command=partial(self.show_menu, canteen_name, shop_name),
        )
        back_button.pack(pady=12)
        ctk.CTkButton(
            self.page_frame, text="กลับไปดูตะกร้าทุกร้าน", command=self.show_cart,
        ).pack(pady=8)

    def show_checkout(self, canteen_name, shop_name):
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
        message = ctk.CTkLabel(
            self.page_frame,
            text=f"เลขคำสั่งซื้อ #{order_id}\n{canteen_name} / {shop_name}\n"
                 "รับแจ้งชำระแล้ว รอตรวจสอบเงินเข้า\nยังไม่ยืนยันการชำระเงินหรือส่งให้ร้านทำอาหาร",
        )
        message.pack(pady=24)
        back_button = ctk.CTkButton(
            self.page_frame, text="กลับไปดูตะกร้า", command=self.show_cart,
        )
        back_button.pack(pady=12)

    def show_shop_orders(self):
        self.clear_page()
        self.page_title_label.configure(text="จัดการออเดอร์ร้านค้า")
        page = ShopOrdersPage(self.page_frame, self.show_canteens)
        page.pack(fill="x")
