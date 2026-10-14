from pathlib import Path

import customtkinter as ctk
from PIL import Image


class PaymentPage(ctk.CTkFrame):
    def __init__(self, parent, shop_name, total_price, on_report, go_back):
        super().__init__(parent, fg_color="transparent")
        self.add_text(f"ชำระเงินร้าน {shop_name} — {total_price} บาท")
        self.add_text("บัญชีทดสอบของผู้พัฒนา — สำหรับสาธิต ยังไม่ต้องโอนเงินจริง")
        self.add_text("ตรวจยอดและชื่อผู้รับในแอปธนาคารก่อนโอน\nQR นี้ไม่ได้ปรับยอดตามตะกร้า")

        qr_file = Path(__file__).resolve().parent.parent / "assets" / "payment_qr.png"
        qr_available = False
        try:
            with Image.open(qr_file) as picture:
                self.qr_image = ctk.CTkImage(
                    light_image=picture.copy(), dark_image=picture.copy(), size=(295, 400),
                )
            qr_label = ctk.CTkLabel(self, text="", image=self.qr_image)
            qr_label.pack(pady=8)
            qr_available = True
        except (OSError, ValueError):
            self.add_text("ไม่พบรูป QR หรือเปิดรูปไม่ได้ กรุณาติดต่อผู้ดูแล")

        self.add_text("การแจ้งชำระยังไม่ใช่การยืนยันเงินเข้า ร้านต้องตรวจสอบก่อนทำอาหาร")
        self.error_label = ctk.CTkLabel(self, text="", wraplength=500)
        self.error_label.pack(pady=4)
        self.report_button = ctk.CTkButton(
            self, text="แจ้งชำระแล้ว (ทดสอบ)", command=on_report,
        )
        self.report_button.pack(pady=8)
        if not qr_available:
            self.report_button.configure(state="disabled")
        back_button = ctk.CTkButton(self, text="กลับไปตรวจรายการ", command=go_back)
        back_button.pack(pady=8)

    def add_text(self, text):
        label = ctk.CTkLabel(self, text=text, wraplength=500)
        label.pack(pady=6)

    def show_error(self, message):
        self.error_label.configure(text=message)
        self.report_button.configure(state="normal")
