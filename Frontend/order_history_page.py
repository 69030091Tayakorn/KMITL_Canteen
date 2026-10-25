import json
import sqlite3
from functools import partial

import customtkinter as ctk

from Backend import order_history
from Backend.shop_orders import status_names

ORANGE = "#F45B2A"
DARK = "#242424"
MUTED = "#777777"


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

    def add_text(self, text, size=15, bold=False, color=DARK, parent=None, pady=6):
        target = parent or self
        label = ctk.CTkLabel(target, text=text, wraplength=900, justify="left", anchor="w",
                             font=ctk.CTkFont(size=size, weight="bold" if bold else "normal"),
                             text_color=color)
        label.pack(fill="x", padx=18, pady=pady)
        return label

    def add_button(self, text, command, primary=False):
        button = ctk.CTkButton(self, text=text, command=command, height=40, width=230, corner_radius=10,
                               fg_color=ORANGE if primary else "#F2F2F2",
                               hover_color="#DF4B20" if primary else "#E7E7E7",
                               text_color="#FFFFFF" if primary else DARK,
                               font=ctk.CTkFont(size=14, weight="bold" if primary else "normal"))
        button.pack(pady=5)
        return button

    def show_orders(self):
        self.clear()
        self.add_text("คำสั่งซื้อของฉัน", size=21, bold=True, pady=(12, 4))
        self.add_text("ตรวจสอบสถานะและรายละเอียดคำสั่งซื้อของคุณ", size=14, color=MUTED, pady=(0, 8))
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=(0, 10))
        ctk.CTkButton(actions, text="รีเฟรชรายการ", command=self.show_orders, height=38, width=170, corner_radius=9, fg_color=ORANGE, hover_color="#DF4B20", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="กลับไปเลือกโรงอาหาร", command=self.go_back, height=38, width=200, corner_radius=9, fg_color="#F2F2F2", hover_color="#E7E7E7", text_color=DARK, font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        try:
            rows = order_history.read_orders()
        except (sqlite3.Error, ValueError):
            self.add_text("อ่านข้อมูลไม่สำเร็จ กรุณาลองรีเฟรชอีกครั้ง", size=15, color="#C0392B")
            return
        if not rows:
            empty = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=14, border_width=1, border_color="#EAEAEA")
            empty.pack(fill="x", padx=12, pady=10)
            self.add_text("ยังไม่มีคำสั่งซื้อ", size=16, color=MUTED, parent=empty, pady=20)
            return
        for order in rows:
            frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=14, border_width=1, border_color="#EAEAEA")
            frame.pack(fill="x", padx=12, pady=7)
            status = status_names.get(order['status'], order['status'])
            self.add_text(f"คำสั่งซื้อ #{order['order_id']}", size=17, bold=True, parent=frame, pady=(12, 2))
            self.add_text(f"{order['canteen_name']} / {order['shop_name']}", size=15, parent=frame, pady=2)
            self.add_text(f"รับ {order['pickup_date']} เวลา {order['pickup_time']}  •  {order['total']} บาท", size=14, parent=frame, pady=2)
            self.add_text(f"สถานะ: {status}", size=14, bold=True, color=ORANGE if order['status'] == 'awaiting_payment_review' else DARK, parent=frame, pady=2)
            ctk.CTkButton(frame, text="ดูรายละเอียด", command=partial(self.show_details, order['order_id']), height=38, width=200, corner_radius=9, fg_color=ORANGE, hover_color="#DF4B20", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=18, pady=(6, 14))

    def show_details(self, order_id):
        self.clear()
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(6, 10))
        ctk.CTkButton(top, text="← กลับรายการคำสั่งซื้อ", command=self.show_orders, height=38, width=220, corner_radius=9, fg_color="#F2F2F2", hover_color="#E7E7E7", text_color=DARK, font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        ctk.CTkButton(top, text="รีเฟรชสถานะ", command=partial(self.show_details, order_id), height=38, width=160, corner_radius=9, fg_color=ORANGE, hover_color="#DF4B20", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        try:
            order, items = order_history.read_details(order_id)
        except (sqlite3.Error, ValueError):
            self.add_text("อ่านข้อมูลไม่สำเร็จ กรุณาลองรีเฟรชอีกครั้ง", size=15, color="#C0392B")
            return
        if order is None:
            self.add_text("ไม่พบคำสั่งซื้อนี้", size=16)
            return
        card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=14, border_width=1, border_color="#EAEAEA")
        card.pack(fill="x", padx=12, pady=5)
        self.add_text(f"คำสั่งซื้อ #{order_id}", size=21, bold=True, parent=card, pady=(16, 4))
        self.add_text(f"{order['canteen_name']} / {order['shop_name']}", size=16, bold=True, parent=card, pady=3)
        self.add_text(f"ผู้รับ: {order['customer_name']}\nวันที่รับ {order['pickup_date']} เวลา {order['pickup_time']}", size=15, parent=card, pady=5)
        status = status_names.get(order['status'], order['status'])
        self.add_text("สถานะ: " + status, size=15, bold=True, color=ORANGE, parent=card, pady=5)
        if order['status'] == 'payment_rejected':
            self.add_text('กรุณาติดต่อร้านเพื่อตรวจสอบยอดที่แจ้งชำระ อย่าโอนซ้ำก่อนตรวจสอบ', size=14, color="#C0392B", parent=card)
        elif order['status'] == 'awaiting_payment_review':
            self.add_text('ร้านยังไม่ได้ยืนยันเงินเข้า', size=14, color="#9A5B00", parent=card)
        self.add_text("รายการอาหาร", size=17, bold=True, parent=card, pady=(12, 4))
        total = 0
        for item in items:
            subtotal = item['unit_price'] * item['quantity']
            total += subtotal
            self.add_text(f"{item['menu_name']}  —  {item['unit_price']} บาท × {item['quantity']} = {subtotal} บาท", size=15, parent=card, pady=4)
            try:
                options = json.loads(item['options'])
                options_text = ', '.join(options)
            except (ValueError, TypeError):
                options_text = str(item['options'])
            if options_text:
                self.add_text('ตัวเลือก: ' + options_text, size=13, color=MUTED, parent=card, pady=2)
            if item['note']:
                self.add_text('หมายเหตุ: ' + item['note'], size=13, color=MUTED, parent=card, pady=2)
        self.add_text(f'ยอดรวม {total} บาท', size=19, bold=True, color=ORANGE, parent=card, pady=(12, 4))
        self.add_text('กดรีเฟรชสถานะเพื่ออ่านข้อมูลล่าสุดจากร้าน', size=13, color=MUTED, parent=card, pady=(2, 16))
