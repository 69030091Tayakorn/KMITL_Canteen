from Backend import users, orders, order_history, shop_orders, catalog, checkout
import unittest
import test_catalog
from datetime import datetime, timedelta


class AccountTests(unittest.TestCase):
    setUp = test_catalog.CatalogTests.setUp
    tearDown = test_catalog.CatalogTests.tearDown

    def test_passwords_and_registration(self):
        with self.assertRaises(ValueError):
            users.register_customer('TESTER', 'password123', 'Duplicate')
        saved = self.connection.execute('SELECT password_hash FROM users').fetchone()[0]
        self.assertNotEqual(saved, 'password123')
        self.assertNotEqual(saved, users.hash_password('password123'))
        with self.assertRaises(ValueError):
            users.login('tester', 'incorrect')
        with self.assertRaises(ValueError):
            users.require_user()
        self.assertEqual(users.login('TESTER', 'password123')['role'], 'customer')
        users.logout()
        with self.assertRaises(ValueError):
            order_history.read_orders()

    def test_order_access_by_customer_and_shop(self):
        item = dict(canteen='คณะครุศาสตร์', shop='ร้านน้ำผลไม้', menu='น้ำส้ม', price=25, quantity=1, options=[], note='')
        date = (datetime.now(checkout.THAI_TIME) + timedelta(days=1)).date().isoformat()
        order_id = orders.save_order(item['canteen'], item['shop'], [item], 'Test', '0812345678', date, '12:00')
        self.assertEqual(order_history.read_orders()[0]['order_id'], order_id)
        users.register_customer('second', 'password123', 'Second')
        users.login('second', 'password123')
        self.assertEqual(order_history.read_orders(), [])
        self.assertEqual(order_history.read_details(order_id), (None, []))
        with self.assertRaises(ValueError):
            shop_orders.change_status(order_id, item['canteen'], item['shop'], 'awaiting_payment_review', 'paid')
        shop_id = catalog.get_shop(item['canteen'], item['shop'])['shop_id']
        other_id = self.connection.execute('SELECT shop_id FROM shops WHERE shop_id != ?', (shop_id,)).fetchone()[0]
        users.create_account('wrongshop', 'password123', 'Other shop', 'shop', other_id)
        users.login('wrongshop', 'password123')
        self.assertEqual(shop_orders.read_orders(item['canteen'], item['shop']), [])
        self.assertEqual(shop_orders.read_items(order_id, item['canteen'], item['shop']), [])
        with self.assertRaises(ValueError):
            shop_orders.change_status(order_id, item['canteen'], item['shop'], 'awaiting_payment_review', 'paid')
        users.create_account('rightshop', 'password123', 'Right shop', 'shop', shop_id)
        users.login('rightshop', 'password123')
        self.assertEqual(len(shop_orders.read_orders(item['canteen'], item['shop'])), 1)
        shop_orders.change_status(order_id, item['canteen'], item['shop'], 'awaiting_payment_review', 'paid')
        with self.assertRaises(ValueError):
            shop_orders.change_status(order_id, item['canteen'], item['shop'], 'awaiting_payment_review', 'paid')
        with self.assertRaises(ValueError):
            orders.save_order(item['canteen'], item['shop'], [item], 'Test', '0812345678', date, '12:00')
        users.login('tester', 'password123')
        self.assertEqual(order_history.read_details(order_id)[0]['status'], 'paid')
