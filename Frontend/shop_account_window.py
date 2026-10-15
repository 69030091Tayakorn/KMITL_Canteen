import sqlite3

import customtkinter as ctk

from Backend import catalog, users


class ShopAccountWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('สร้างบัญชีร้าน — ผู้ดูแลเครื่อง')
        self.geometry('620x650')
        self.minsize(560, 600)
        ctk.CTkLabel(self, text='สร้างบัญชีร้านค้า', font=ctk.CTkFont(size=24)).pack(pady=16)
        ctk.CTkLabel(self, text='เลือกร้านที่บัญชีนี้จะดูแล').pack(pady=4)
        self.shop_ids = {}
        error = ''
        try:
            shops = catalog.read_rows('''
                SELECT shops.shop_id, canteens.name AS canteen, shops.name AS shop
                FROM shops JOIN canteens USING(canteen_id) ORDER BY shops.shop_id
            ''')
            for shop in shops:
                label = f"{shop['shop_id']}: {shop['canteen']} / {shop['shop']}"
                self.shop_ids[label] = shop['shop_id']
        except sqlite3.Error:
            error = 'อ่านร้านไม่ได้ กรุณาบันทึกงานใน DB Browser แล้วเปิดหน้าต่างนี้ใหม่'
        self.shop_menu = ctk.CTkOptionMenu(self, values=list(self.shop_ids) or ['ไม่มีร้าน'], width=500)
        self.shop_menu.pack(pady=8)
        self.username_entry = self.add_entry('ชื่อผู้ใช้ (3–40 ตัวอักษร)')
        self.name_entry = self.add_entry('ชื่อแสดง')
        self.password_entry = self.add_entry('รหัสผ่าน (8–128 ตัวอักษร)', password=True)
        self.confirm_entry = self.add_entry('ยืนยันรหัสผ่าน', password=True)
        self.show_password = ctk.CTkCheckBox(self, text='แสดงรหัสผ่าน', command=self.toggle_password)
        self.show_password.pack(pady=12)
        self.message_label = ctk.CTkLabel(self, text=error, wraplength=500)
        self.message_label.pack(pady=8)
        self.create_button = ctk.CTkButton(self, text='สร้างบัญชีร้าน', command=self.create_account)
        self.create_button.pack(pady=8)
        if not self.shop_ids:
            self.create_button.configure(state='disabled')

    def add_entry(self, title, password=False):
        ctk.CTkLabel(self, text=title).pack(pady=(8, 0))
        entry = ctk.CTkEntry(self, width=360, show='*' if password else '')
        entry.pack(pady=4)
        return entry

    def toggle_password(self):
        symbol = '' if self.show_password.get() else '*'
        self.password_entry.configure(show=symbol)
        self.confirm_entry.configure(show=symbol)

    def create_account(self):
        password = self.password_entry.get()
        if password != self.confirm_entry.get():
            self.message_label.configure(text='รหัสผ่านทั้งสองช่องไม่ตรงกัน')
            return
        shop_id = self.shop_ids.get(self.shop_menu.get())
        if shop_id is None:
            self.message_label.configure(text='กรุณาเลือกร้าน')
            return
        self.create_button.configure(state='disabled')
        try:
            users.create_account(
                self.username_entry.get(), password, self.name_entry.get(), 'shop', shop_id,
            )
        except ValueError as error:
            self.message_label.configure(text=str(error))
            self.create_button.configure(state='normal')
        except sqlite3.Error:
            self.message_label.configure(text='บันทึกไม่ได้ กรุณาบันทึกงานใน DB Browser แล้วลองใหม่')
            self.create_button.configure(state='normal')
        else:
            self.password_entry.delete(0, 'end')
            self.confirm_entry.delete(0, 'end')
            self.message_label.configure(text='สร้างบัญชีสำเร็จ กลับไปเข้าสู่ระบบในแอป KMITL Canteen ได้เลย')
