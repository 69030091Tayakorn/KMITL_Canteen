import sqlite3

import customtkinter as ctk

from Backend import users


class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, on_login):
        super().__init__(parent, fg_color='transparent')
        self.on_login = on_login
        self.show_form()

    def add_entry(self, title, password=False):
        ctk.CTkLabel(self, text=title).pack(pady=(8, 0))
        entry = ctk.CTkEntry(self, width=320, show='*' if password else '')
        entry.pack(pady=4)
        return entry

    def show_form(self, register=False):
        for widget in self.winfo_children():
            widget.destroy()
        self.register = register
        title = 'สมัครสมาชิกสำหรับลูกค้า' if register else 'เข้าสู่ระบบ'
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=22)).pack(pady=8)
        self.username_entry = self.add_entry('ชื่อผู้ใช้')
        self.password_entry = self.add_entry('รหัสผ่าน (8–128 ตัวอักษร)', password=True)
        if register:
            self.confirm_entry = self.add_entry('ยืนยันรหัสผ่าน', password=True)
            self.name_entry = self.add_entry('ชื่อแสดงในแอป')
        self.error_label = ctk.CTkLabel(self, text='', wraplength=500)
        self.error_label.pack(pady=8)
        self.submit_button = ctk.CTkButton(self, text=title, command=self.submit)
        self.submit_button.pack(pady=8)
        switch_text = 'กลับไปเข้าสู่ระบบ' if register else 'ยังไม่มีบัญชี — สมัครสมาชิก'
        ctk.CTkButton(self, text=switch_text, command=lambda: self.show_form(not register)).pack(pady=8)
        self.username_entry.focus_set()

    def submit(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.submit_button.configure(state='disabled')
        try:
            if self.register:
                if password != self.confirm_entry.get():
                    raise ValueError('รหัสผ่านทั้งสองช่องไม่ตรงกัน')
                users.register_customer(username, password, self.name_entry.get())
                self.show_form()
                self.username_entry.insert(0, username.strip())
                self.error_label.configure(text='สมัครสำเร็จ กรุณาเข้าสู่ระบบ')
                return
            user = users.login(username, password)
        except ValueError as error:
            self.error_label.configure(text=str(error))
        except sqlite3.Error:
            self.error_label.configure(text='เปิดข้อมูลบัญชีไม่ได้ กรุณาตรวจตาราง users และบันทึกงานใน DB Browser')
        else:
            self.on_login(user)
            return
        self.submit_button.configure(state='normal')
