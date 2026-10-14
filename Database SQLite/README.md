# จัดการข้อมูลใน DB Browser for SQLite

เปิด canteen.db ที่อยู่ในโฟลเดอร์นี้ งานประจำไม่ต้องรัน schema.sql หรือ sample_data.sql ซ้ำ

## ดูข้อมูล

ใช้ Browse Data เลือกตาราง หรือรันใน Execute SQL:

```sql
SELECT * FROM canteens;
SELECT * FROM shops;
SELECT menu_id, shop_id, name, price, is_available, menu_type FROM menu_items;
```

## แก้ราคาและสถานะ

ตรวจ menu_id ก่อน ตัวอย่างเลข 1 ด้านล่างต้องเปลี่ยนเป็นเมนูที่ต้องการจริง

```sql
UPDATE menu_items SET price = 50 WHERE menu_id = 1;
UPDATE menu_items SET is_available = 0 WHERE menu_id = 1;
-- 0 = หมด, 1 = พร้อมขาย
```

## เพิ่มโรงอาหาร ร้าน และเมนู

รันทีละขั้นแล้วดูรหัสที่สร้างได้ ห้ามเดารหัสจากตัวอย่าง

```sql
INSERT INTO canteens(name) VALUES ('โรงอาหารตัวอย่างใหม่');
SELECT * FROM canteens;

-- แทนเลข 1 ด้วย canteen_id ที่ต้องการ
INSERT INTO shops(canteen_id, name, shop_type)
VALUES (1, 'ร้านตัวอย่างใหม่', 'regular');
SELECT * FROM shops;

-- แทนเลข 1 ด้วย shop_id ของร้านที่ต้องการ
INSERT INTO menu_items(shop_id, name, price, is_available, menu_type)
VALUES (1, 'เมนูตัวอย่างใหม่', 40, 1, 'regular');
```

กด Write Changes ทุกครั้งก่อนกลับไปแอป ถ้าแก้ค้างไว้ DB Browser อาจล็อกการบันทึกจากแอป

## ประเภทเมนู

- ร้านทั่วไปใช้ shop_type = regular และ menu_type = regular
- ร้านข้าวแกงใช้ shop_type = curry
- กับข้าวใช้ menu_type = curry_dish และ price = 0 เพราะคิดราคาแบบราด
- ราคาแบบราดใช้ menu_type = curry_price และ dish_count = 1 หรือ 2
- เพิ่มข้าวใช้ menu_type = extra_rice
- menu_options เก็บตัวเลือกตามกลุ่มของร้านและราคาเพิ่ม ไม่แสดง +0 บาทในแอป

เปิด Foreign Keys ในแท็บ Edit Pragmas หรือรัน `PRAGMA foreign_keys = ON;` ก่อนเริ่มแก้ไข transaction เพื่อให้ SQLite ตรวจรหัสอ้างอิง

ออเดอร์เก่าเก็บชื่อและราคาขณะสั่ง การแก้เมนูไม่ควรแก้ประวัติ orders/order_items ตามไปด้วย
