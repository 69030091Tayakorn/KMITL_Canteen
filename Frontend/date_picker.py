import calendar
from datetime import date, datetime
from functools import partial

import customtkinter as ctk

from Backend.checkout import THAI_TIME


class DatePicker(ctk.CTkToplevel):
    """ปฏิทินเลือกวันที่ แล้วส่งวันที่กลับให้หน้ากรอกข้อมูล"""

    def __init__(self, parent, selected_date, on_select):
        super().__init__(parent)
        self.title("เลือกวันที่รับอาหาร")
        self.configure(fg_color="#FFFFFF")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.on_select = on_select
        self.selected_date = selected_date
        today = datetime.now(THAI_TIME).date()
        start_date = selected_date or today
        self.year = start_date.year
        self.month = start_date.month

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=12)
        self.previous_button = ctk.CTkButton(
            header, text="‹", width=40, command=partial(self.change_month, -1),
            fg_color="#F45B2A", hover_color="#DF4B20", text_color="#FFFFFF",
        )
        self.previous_button.pack(side="left")
        self.month_label = ctk.CTkLabel(header, text="", width=230)
        self.month_label.pack(side="left", padx=8)
        next_button = ctk.CTkButton(
            header, text="›", width=40, command=partial(self.change_month, 1),
            fg_color="#F45B2A", hover_color="#DF4B20", text_color="#FFFFFF",
        )
        next_button.pack(side="right")

        self.days_frame = ctk.CTkFrame(self)
        self.days_frame.pack(padx=12, pady=8)
        cancel_button = ctk.CTkButton(
            self, text="ยกเลิก", command=self.destroy,
            fg_color="#FFFFFF", hover_color="#FFF4EE", text_color="#F45B2A",
            border_width=1, border_color="#F45B2A",
        )
        cancel_button.pack(pady=12)
        self.show_month()
        self.after(100, self.focus_calendar)

    def focus_calendar(self):
        self.grab_set()
        self.focus_force()

    def change_month(self, amount):
        self.month += amount
        if self.month == 0:
            self.month = 12
            self.year -= 1
        elif self.month == 13:
            self.month = 1
            self.year += 1
        self.show_month()

    def show_month(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                  "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        self.month_label.configure(text=f"{months[self.month - 1]} {self.year} (ค.ศ.)")
        today = datetime.now(THAI_TIME).date()
        if (self.year, self.month) <= (today.year, today.month):
            self.previous_button.configure(state="disabled")
        else:
            self.previous_button.configure(state="normal")

        weekdays = ["จ", "อ", "พ", "พฤ", "ศ", "ส", "อา"]
        for column, weekday in enumerate(weekdays):
            label = ctk.CTkLabel(self.days_frame, text=weekday)
            label.grid(row=0, column=column, padx=4, pady=4)

        weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(self.year, self.month)
        for row, week in enumerate(weeks, start=1):
            for column, day in enumerate(week):
                if day == 0:
                    continue
                day_date = date(self.year, self.month, day)
                button = ctk.CTkButton(
                    self.days_frame, text=str(day), width=40, height=36,
                    command=partial(self.select_date, day_date),
                    fg_color="#F45B2A", hover_color="#DF4B20",
                    text_color="#FFFFFF", corner_radius=8,
                )
                button.grid(row=row, column=column, padx=4, pady=4)
                if day_date < today:
                    button.configure(state="disabled")
                if day_date == self.selected_date:
                    button.configure(border_width=2, border_color="#242424")

    def select_date(self, selected_date):
        # ตรวจอีกครั้ง เผื่อเปิดปฏิทินค้างข้ามวัน
        if selected_date < datetime.now(THAI_TIME).date():
            self.show_month()
            return
        self.on_select(selected_date)
        self.destroy()
