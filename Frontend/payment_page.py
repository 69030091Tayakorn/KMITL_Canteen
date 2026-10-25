from pathlib import Path

import customtkinter as ctk
from PIL import Image


class PaymentPage(ctk.CTkFrame):
    def __init__(self, parent, shop_name, total_price, on_report, go_back):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#EAEAEA")
        ctk.CTkLabel(self, text="ชำระเงิน", font=ctk.CTkFont(size=22, weight="bold"), text_color="#242424").pack(pady=(20, 4))
        ctk.CTkLabel(self, text=f"ร้าน {shop_name}", font=ctk.CTkFont(size=16), text_color="#555555").pack(pady=3)
        ctk.CTkLabel(self, text=f"ยอดที่ต้องชำระ  {total_price} บาท", font=ctk.CTkFont(size=20, weight="bold"), text_color="#F45B2A").pack(pady=(4, 12))
        self.add_text("บัญชีทดสอบของผู้พัฒนา — สำหรับสาธิต ยังไม่ต้องโอนเงินจริง", size=14, color="#555555")
        self.add_text("ตรวจยอดและชื่อผู้รับในแอปธนาคารก่อนโอน\nQR นี้ไม่ได้ปรับยอดตามตะกร้า", size=14, color="#9A5B00")

        qr_file = Path(__file__).resolve().parent.parent / "assets" / "payment_qr.png"
        try:
            with Image.open(qr_file) as picture:
                self.qr_image = ctk.CTkImage(light_image=picture.copy(), dark_image=picture.copy(), size=(240, 325))
            ctk.CTkLabel(self, text="", image=self.qr_image).pack(pady=8)
        except (OSError, ValueError):
            # Demo mode: QR is optional. Let the user continue without a QR image.
            placeholder = ctk.CTkFrame(self, width=240, height=150, fg_color="#FFF0E9", corner_radius=12)
            placeholder.pack(pady=8)
            placeholder.pack_propagate(False)
            ctk.CTkLabel(placeholder, text="QR CODE\n(จำลอง)", font=ctk.CTkFont(size=22, weight="bold"), text_color="#F45B2A", justify="center").pack(expand=True)
            self.add_text("ไม่มีรูป QR — โหมดสาธิตยังสามารถกดดำเนินการต่อได้", size=13, color="#9A5B00")

        self.add_text("การแจ้งชำระยังไม่ใช่การยืนยันเงินเข้า ร้านต้องตรวจสอบก่อนทำอาหาร", size=13, color="#555555")
        self.error_label = ctk.CTkLabel(self, text="", wraplength=800, font=ctk.CTkFont(size=14), text_color="#C0392B")
        self.error_label.pack(pady=5)
        self.report_button = ctk.CTkButton(self, text="แจ้งชำระแล้ว (ทดสอบ)", command=on_report, width=280, height=42, corner_radius=10, fg_color="#F45B2A", hover_color="#DF4B20", font=ctk.CTkFont(size=15, weight="bold"))
        self.report_button.pack(pady=6)
        ctk.CTkButton(self, text="กลับไปตรวจรายการ", command=go_back, width=280, height=38, corner_radius=10, fg_color="#F2F2F2", hover_color="#E7E7E7", text_color="#333333", font=ctk.CTkFont(size=14)).pack(pady=(2, 18))

    def add_text(self, text, size=15, color="#333333"):
        ctk.CTkLabel(self, text=text, wraplength=800, font=ctk.CTkFont(size=size), text_color=color, justify="center").pack(pady=5)

    def show_error(self, message):
        self.error_label.configure(text=message)
        self.report_button.configure(state="normal")
