import sqlite3

import customtkinter as ctk

from Backend import cart, checkout, orders, catalog
from Frontend.date_picker import DatePicker
from Frontend.payment_page import PaymentPage


class CheckoutPage(ctk.CTkFrame):
    def __init__(self, parent, canteen_name, shop_name, items, go_back, on_saved):
        super().__init__(parent, fg_color="transparent")

        self.canteen_name = canteen_name
        self.shop_name = shop_name
        self.items = items
        self.go_back = go_back
        self.on_saved = on_saved
        self.order_id = None
        self.payment_page = None
        self.review_frame = None
        self.selected_date = None
        self.calendar_window = None

        self.create_form()

    # 1. สร้างหน้ากรอกข้อมูลผู้รับอาหาร
    def create_form(self):
        self.form_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#EAEAEA")
        self.form_frame.pack(fill="x", padx=18, pady=10)

        title_label = ctk.CTkLabel(
            self.form_frame,
            text="กรอกข้อมูลเพื่อรับอาหาร",
            font=ctk.CTkFont(size=21, weight="bold"), text_color="#242424",
        )
        title_label.pack(pady=(20, 6))
        ctk.CTkLabel(self.form_frame, text="ตรวจสอบข้อมูลก่อนดำเนินการสั่งซื้อ", font=ctk.CTkFont(size=14), text_color="#777777").pack(pady=(0, 12))

        self.name_entry = self.create_entry("ชื่อผู้รับอาหาร", "ชื่อผู้รับ")
        self.phone_entry = self.create_entry("เบอร์โทร 10 หลัก", "เช่น 0812345678")
        self.create_pickup_controls()

        self.error_label = ctk.CTkLabel(self.form_frame, text="", wraplength=760, font=ctk.CTkFont(size=14), text_color="#C0392B")
        self.error_label.pack(pady=10)

        review_button = ctk.CTkButton(
            self.form_frame,
            text="ตรวจรายการก่อนสั่ง", height=42, width=260, corner_radius=10,
            fg_color="#F45B2A", hover_color="#DF4B20", font=ctk.CTkFont(size=15, weight="bold"),
            command=self.check_form,
        )
        review_button.pack(pady=(8, 6))

        back_button = ctk.CTkButton(
            self.form_frame,
            text="กลับไปตะกร้าร้านนี้", height=38, width=260, corner_radius=10,
            fg_color="#F2F2F2", hover_color="#E7E7E7", text_color="#333333", font=ctk.CTkFont(size=14),
            command=self.go_back,
        )
        back_button.pack(pady=(4, 20))

    def create_pickup_controls(self):
        date_label = ctk.CTkLabel(self.form_frame, text="วันที่รับอาหาร", font=ctk.CTkFont(size=15, weight="bold"), text_color="#333333")
        date_label.pack(pady=(8, 0))
        self.date_button = ctk.CTkButton(
            self.form_frame, text="เลือกวันจากปฏิทิน", width=400, height=40, corner_radius=9, font=ctk.CTkFont(size=14),
            command=self.open_calendar,
        )
        self.date_button.pack(pady=4)

        time_label = ctk.CTkLabel(self.form_frame, text="เวลารับ (เวลาไทย แบบ 24 ชั่วโมง)", font=ctk.CTkFont(size=15, weight="bold"), text_color="#333333")
        time_label.pack(pady=(8, 0))
        time_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        time_frame.pack(pady=4)
        hours = [f"{hour:02d}" for hour in range(24)]
        minutes = [f"{minute:02d}" for minute in range(60)]
        self.hour_menu = ctk.CTkOptionMenu(time_frame, values=hours, width=180, height=38, font=ctk.CTkFont(size=14))
        self.hour_menu.set("ชั่วโมง")
        self.hour_menu.pack(side="left", padx=4)
        self.minute_menu = ctk.CTkOptionMenu(time_frame, values=minutes, width=180, height=38, font=ctk.CTkFont(size=14))
        self.minute_menu.set("นาที")
        self.minute_menu.pack(side="left", padx=4)

    def open_calendar(self):
        if self.calendar_window is not None and self.calendar_window.winfo_exists():
            self.calendar_window.lift()
            return
        self.calendar_window = DatePicker(self, self.selected_date, self.select_date)

    def select_date(self, selected_date):
        self.selected_date = selected_date
        self.date_button.configure(text=selected_date.strftime("%d/%m/%Y (ค.ศ.)"))

    # สร้างชื่อช่องและช่องกรอก ใช้กับชื่อและเบอร์โทร
    def create_entry(self, label_text, example):
        label = ctk.CTkLabel(self.form_frame, text=label_text, font=ctk.CTkFont(size=15, weight="bold"), text_color="#333333")
        label.pack(pady=(10, 2))

        entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text=example,
            width=400, height=40, font=ctk.CTkFont(size=14), corner_radius=9,
        )
        entry.pack(pady=4)
        return entry

    # 2. อ่านข้อมูลจากช่องกรอก แล้วให้ Backend ตรวจ
    def check_form(self):
        if not self.items:
            self.error_label.configure(text="ตะกร้าว่าง กรุณาเพิ่มอาหารก่อน")
            return

        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        if self.selected_date is None:
            self.error_label.configure(text="กรุณาเลือกวันที่รับอาหารจากปฏิทิน")
            return
        hour = self.hour_menu.get()
        minute = self.minute_menu.get()
        if hour == "ชั่วโมง" or minute == "นาที":
            self.error_label.configure(text="กรุณาเลือกชั่วโมงและนาทีที่จะรับอาหาร")
            return
        pickup_date = self.selected_date.isoformat()
        pickup_time = hour + ":" + minute

        error = checkout.check_details(name, phone, pickup_date, pickup_time)
        self.error_label.configure(text=error)
        if error:
            return

        self.show_review(name, phone, pickup_date, pickup_time)

    # 3. แสดงข้อมูลที่ผ่านการตรวจ พร้อมอาหารและยอดรวม
    def show_review(self, name, phone, pickup_date, pickup_time):
        self.order_details = (name, phone, pickup_date, pickup_time)
        # ซ่อนฟอร์มแทนการลบ เพื่อเก็บข้อความที่กรอกไว้
        self.form_frame.pack_forget()
        self.review_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#EAEAEA")
        self.review_frame.pack(fill="x", padx=18, pady=10)

        self.add_review_text(f"ตรวจรายการ: {self.canteen_name} / {self.shop_name}")
        self.add_review_text(f"ผู้รับ: {name}")
        self.add_review_text(f"เบอร์โทร: {phone}")
        self.add_review_text(f"รับวันที่ {pickup_date} เวลา {pickup_time} (ไทย)")

        for item in self.items:
            self.show_food_item(item)

        total_price = cart.get_total_price(self.items)
        self.add_review_text(f"ยอดรวมร้านนี้ {total_price} บาท")
        self.add_review_text("ยังไม่ได้ส่งออเดอร์หรือชำระเงิน")

        self.save_error_label = ctk.CTkLabel(self.review_frame, text="", wraplength=800, font=ctk.CTkFont(size=14), text_color="#C0392B")
        self.save_error_label.pack(pady=10)
        self.confirm_button = ctk.CTkButton(
            self.review_frame, text="ไปหน้าชำระเงิน", width=260, height=42, corner_radius=10,
            fg_color="#F45B2A", hover_color="#DF4B20", font=ctk.CTkFont(size=15, weight="bold"), command=self.show_payment,
        )
        self.confirm_button.pack(pady=(10, 6))

        edit_button = ctk.CTkButton(
            self.review_frame,
            text="แก้ไขข้อมูลผู้รับ", width=260, height=38, corner_radius=10,
            fg_color="#F2F2F2", hover_color="#E7E7E7", text_color="#333333", font=ctk.CTkFont(size=14), command=self.edit_details,
        )
        edit_button.pack(pady=6)

        back_button = ctk.CTkButton(
            self.review_frame,
            text="กลับไปแก้ไขตะกร้า", width=260, height=38, corner_radius=10,
            fg_color="#F2F2F2", hover_color="#E7E7E7", text_color="#333333", font=ctk.CTkFont(size=14), command=self.go_back,
        )
        back_button.pack(pady=(6, 20))

    def show_payment(self):
        try:
            for item in self.items:
                catalog.check_cart_item(item)
        except (ValueError, sqlite3.Error) as error:
            self.save_error_label.configure(text=str(error))
            return
        error = checkout.check_details(*self.order_details)
        if error:
            self.save_error_label.configure(text=error)
            return
        self.review_frame.pack_forget()
        self.payment_page = PaymentPage(
            self, self.shop_name, cart.get_total_price(self.items),
            self.confirm_order, self.back_to_review,
        )
        self.payment_page.pack(fill="x")

    def back_to_review(self):
        self.payment_page.destroy()
        self.payment_page = None
        self.review_frame.pack(fill="x")

    def confirm_order(self):
        if self.order_id is not None:
            return
        if self.payment_page is None:
            return
        self.payment_page.report_button.configure(state="disabled")
        try:
            self.order_id = orders.save_order(
                self.canteen_name, self.shop_name, self.items, *self.order_details,
            )
        except ValueError as error:
            self.payment_page.show_error(str(error))
            return
        except (sqlite3.Error, OSError):
            self.payment_page.show_error(
                "บันทึกไม่สำเร็จ ตะกร้ายังอยู่ กรุณาปิดการแก้ไขใน DB Browser แล้วลองใหม่",
            )
            return
        self.on_saved(self.order_id)

    # แสดงอาหารทีละรายการ แยกชื่อ ราคา ตัวเลือก และหมายเหตุ
    def show_food_item(self, item):
        menu_name = item["menu"]
        price = item["price"]
        quantity = item["quantity"]
        item_total = cart.get_item_total(item)

        self.add_review_text(f"{menu_name} — {price} บาท × {quantity} = {item_total} บาท")

        if item["options"]:
            options_text = ", ".join(item["options"])
            self.add_review_text("ตัวเลือก: " + options_text)

        if item["note"]:
            self.add_review_text("หมายเหตุ: " + item["note"])

    def add_review_text(self, text):
        label = ctk.CTkLabel(
            self.review_frame,
            text=text,
            wraplength=850,
            justify="left", font=ctk.CTkFont(size=15), text_color="#333333",
        )
        label.pack(pady=8)

    # 4. กลับไปแก้ข้อมูล โดยไม่ต้องกรอกใหม่
    def edit_details(self):
        self.review_frame.destroy()
        self.review_frame = None
        self.form_frame.pack(fill="x")
