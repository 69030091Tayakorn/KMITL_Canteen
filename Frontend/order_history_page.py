import json
import sqlite3
from functools import partial

import customtkinter as ctk

from Backend import order_history
from Backend.shop_orders import status_names


class OrderHistoryPage(ctk.CTkFrame):
    def __init__(self, parent, go_back, order_id=None):
        super().__init__(parent, fg_color="transparent")
        self.go_back = go_back
        if order_id is None:
            self.show_orders()
        else:
            self.show_details(order_id)

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def add_text(self, text):
        label = ctk.CTkLabel(self, text=text, wraplength=600, justify="left")
        label.pack(pady=6)

    def add_button(self, text, command):
        button = ctk.CTkButton(self, text=text, command=command)
        button.pack(pady=6)

    def show_orders(self):
        self.clear()
        self.add_text('คำสั่งซื้อของฉัน')
        self.add_button('รีเฟรชรายการ', self.show_orders)
        self.add_button('กลับไปเลือกโรงอาหาร', self.go_back)
        try:
            rows = order_history.read_orders()
        except (sqlite3.Error, ValueError):
            self.add_text('อ่านข้อมูลไม่สำเร็จ กรุณาลองรีเฟรชอีกครั้ง')
            return
        if not rows:
            self.add_text('ยังไม่มีคำสั่งซื้อ')
        for order in rows:
            frame = ctk.CTkFrame(self)
            frame.pack(fill="x", pady=6)
            status = status_names.get(order['status'], order['status'])
            text = (
                f"#{order['order_id']} — {order['canteen_name']} / {order['shop_name']}\n"
                f"รับ {order['pickup_date']} เวลา {order['pickup_time']} | {order['total']} บาท\n"
                f"สถานะ: {status}"
            )
            label = ctk.CTkLabel(frame, text=text, wraplength=600, justify="left")
            label.pack(pady=8)
            button = ctk.CTkButton(frame, text='ดูรายละเอียด', command=partial(self.show_details, order['order_id']))
            button.pack(pady=8)

    def show_details(self, order_id):
        self.clear()
        self.add_button('กลับรายการคำสั่งซื้อ', self.show_orders)
        self.add_button('รีเฟรชสถานะ', partial(self.show_details, order_id))
        try:
            order, items = order_history.read_details(order_id)
        except (sqlite3.Error, ValueError):
            self.add_text('อ่านข้อมูลไม่สำเร็จ กรุณาลองรีเฟรชอีกครั้ง')
            return
        if order is None:
            self.add_text('ไม่พบคำสั่งซื้อนี้')
            return
        self.add_text(f"คำสั่งซื้อ #{order_id} — {order['canteen_name']} / {order['shop_name']}")
        self.add_text(f"ผู้รับ: {order['customer_name']}\nวันที่รับ {order['pickup_date']} เวลา {order['pickup_time']}")
        status = status_names.get(order['status'], order['status'])
        self.add_text('สถานะ: ' + status)
        if order['status'] == 'payment_rejected':
            self.add_text('กรุณาติดต่อร้านเพื่อตรวจสอบยอดที่แจ้งชำระ อย่าโอนซ้ำก่อนตรวจสอบ')
        elif order['status'] == 'awaiting_payment_review':
            self.add_text('ร้านยังไม่ได้ยืนยันเงินเข้า')
        total = 0
        for item in items:
            subtotal = item['unit_price'] * item['quantity']
            total += subtotal
            self.add_text(f"{item['menu_name']} — {item['unit_price']} บาท × {item['quantity']} = {subtotal} บาท")
            try:
                options = json.loads(item['options'])
                options_text = ', '.join(options)
            except (ValueError, TypeError):
                options_text = str(item['options'])
            if options_text:
                self.add_text('ตัวเลือก: ' + options_text)
            if item['note']:
                self.add_text('หมายเหตุ: ' + item['note'])
        self.add_text(f'ยอดรวม {total} บาท')
        self.add_text('กดรีเฟรชสถานะเพื่ออ่านข้อมูลล่าสุดจากร้าน')
