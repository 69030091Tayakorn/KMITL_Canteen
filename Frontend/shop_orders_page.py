import json
import sqlite3
from functools import partial
from tkinter import messagebox

import customtkinter as ctk

from Backend import users, shop_orders


class ShopOrdersPage(ctk.CTkFrame):
    def __init__(self, parent, go_back):
        super().__init__(parent, fg_color="transparent")
        self.go_back = go_back
        self.show_shops()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def label(self, text):
        label = ctk.CTkLabel(self, text=text, wraplength=600, justify="left")
        label.pack(pady=6)

    def button(self, text, command):
        button = ctk.CTkButton(self, text=text, command=command)
        button.pack(pady=6)

    def show_shops(self):
        self.clear()
        try:
            shop = users.get_my_shop()
        except (ValueError, sqlite3.Error) as error:
            self.label(str(error))
            self.button('ออกจากระบบ', self.go_back)
            return
        self.canteen = shop['canteen_name']
        self.shop = shop['shop_name']
        self.show_orders()

    def show_orders(self):
        self.clear()
        self.label(f'{self.canteen} / {self.shop}')
        self.button('รีเฟรชรายการ', self.show_orders)
        self.button('ออกจากระบบ', self.go_back)
        try:
            rows = shop_orders.read_orders(self.canteen, self.shop)
        except (sqlite3.Error, ValueError):
            self.label('อ่านออเดอร์ไม่สำเร็จ กรุณาลองใหม่')
            return
        if not rows:
            self.label('ยังไม่มีออเดอร์ของร้านนี้')
        for order in rows:
            status = shop_orders.status_names.get(order['status'], order['status'])
            text = f"#{order['order_id']} | {order['customer_name']} | {order['total']} บาท | {status}"
            self.button(text, partial(self.show_details, order['order_id']))

    def show_details(self, order_id):
        self.clear()
        self.button('กลับรายการออเดอร์', self.show_orders)
        try:
            rows = shop_orders.read_orders(self.canteen, self.shop)
            order = next((row for row in rows if row['order_id'] == order_id), None)
            if order is None:
                self.label('ไม่พบออเดอร์ของร้านนี้')
                return
            items = shop_orders.read_items(order_id, self.canteen, self.shop)
        except (sqlite3.Error, ValueError):
            self.label('อ่านรายละเอียดไม่สำเร็จ กรุณาลองใหม่')
            return
        self.label(f"ออเดอร์ #{order_id} — {self.shop}")
        self.label(f"ผู้รับ: {order['customer_name']} | โทร: {order['phone']}")
        self.label(f"รับวันที่ {order['pickup_date']} เวลา {order['pickup_time']}")
        for item in items:
            self.label(f"{item['menu_name']} × {item['quantity']} = {item['unit_price'] * item['quantity']} บาท")
            try:
                options = json.loads(item['options'])
                self.label('ตัวเลือก: ' + ', '.join(options))
            except (ValueError, TypeError):
                self.label('ตัวเลือก: ' + str(item['options']))
            if item['note']:
                self.label('หมายเหตุ: ' + item['note'])
        self.label(f"ยอดรวม {order['total']} บาท")
        status = order['status']
        self.label('สถานะ: ' + shop_orders.status_names.get(status, status))
        if status == 'awaiting_payment_review':
            self.label('ยังไม่มีสลิปในระบบ ต้องตรวจเงินเข้าจากช่องทางธนาคารเอง\nสำหรับสาธิตเท่านั้น ปุ่มนี้ไม่ตรวจเงินอัตโนมัติ')
        actions = {
            'paid': 'ตรวจเงินเข้าแล้ว — ยืนยัน',
            'payment_rejected': 'ยังยืนยันการชำระเงินไม่ได้',
            'awaiting_payment_review': 'นำกลับมาตรวจชำระอีกครั้ง',
            'preparing': 'รับออเดอร์และเริ่มเตรียม',
            'ready': 'อาหารพร้อมรับ',
            'completed': 'ส่งอาหารให้ผู้รับแล้ว',
        }
        for target in shop_orders.next_statuses.get(status, ()):
            self.button(actions[target], partial(self.update_status, order_id, status, target))

    def update_status(self, order_id, old_status, new_status):
        if new_status == 'paid':
            confirmed = messagebox.askyesno(
                'ยืนยันการตรวจรับเงิน',
                'คุณตรวจชื่อผู้โอนและยอดเงินเข้าครบแล้วใช่ไหม?\nระบบนี้ไม่ตรวจธนาคารอัตโนมัติ',
                parent=self,
            )
            if not confirmed:
                return
        try:
            shop_orders.change_status(order_id, self.canteen, self.shop, old_status, new_status)
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror('เปลี่ยนสถานะไม่สำเร็จ', str(error), parent=self)
        self.show_details(order_id)
