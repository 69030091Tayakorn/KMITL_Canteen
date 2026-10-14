import sqlite3
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch

from Backend import catalog, database, orders, checkout


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.uri = 'file:catalog_test?mode=memory&cache=shared'
        self.connection = sqlite3.connect(self.uri, uri=True)
        root = Path(__file__).resolve().parent.parent / 'Database SQLite'
        self.connection.executescript((root / 'schema.sql').read_text(encoding='utf-8'))
        self.connection.executescript((root / 'sample_data.sql').read_text(encoding='utf-8'))
        def connect():
            connection = sqlite3.connect(self.uri, uri=True)
            connection.execute('PRAGMA foreign_keys=ON')
            return connection
        self.patcher = patch.object(database, 'connect_database', connect)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.connection.close()

    def test_sql_changes_are_read_by_app(self):
        shop = catalog.get_shop('คณะครุศาสตร์', 'ร้านน้ำผลไม้')
        item = catalog.get_menu_items(shop['shop_id'])[0]
        self.connection.execute('UPDATE menu_items SET price=99 WHERE menu_id=?', (item['menu_id'],))
        self.connection.commit()
        data = catalog.get_menu_data('คณะครุศาสตร์', 'ร้านน้ำผลไม้')
        self.assertEqual(data[1]['ร้านน้ำผลไม้'][item['name']], 99)
        self.connection.execute('UPDATE menu_items SET is_available=0 WHERE menu_id=?', (item['menu_id'],))
        self.connection.commit()
        data = catalog.get_menu_data('คณะครุศาสตร์', 'ร้านน้ำผลไม้')
        self.assertNotIn(item['name'], data[1]['ร้านน้ำผลไม้'])

    def test_order_snapshot_and_rollback(self):
        item = dict(canteen='คณะครุศาสตร์',shop='ร้านน้ำผลไม้',menu='น้ำส้ม',price=25,quantity=2,options=[],note='')
        date = (datetime.now(checkout.THAI_TIME)+timedelta(days=1)).date().isoformat()
        orders.save_order(item['canteen'],item['shop'],[item],'Test','0812345678',date,'12:00')
        self.connection.execute("CREATE TRIGGER reject_insert BEFORE INSERT ON order_items BEGIN SELECT RAISE(ABORT,'test'); END")
        self.connection.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            orders.save_order(item['canteen'],item['shop'],[item],'Test','0812345678',date,'12:00')
        self.assertEqual(self.connection.execute('SELECT count(*) FROM orders').fetchone()[0],1)
        self.connection.execute("UPDATE menu_items SET price=50 WHERE name='น้ำส้ม'")
        self.connection.commit()
        with self.assertRaises(ValueError):
            catalog.check_cart_item(item)
        self.assertEqual(self.connection.execute('SELECT unit_price FROM order_items').fetchone()[0],25)

    def test_sql_constraints_and_no_sample_recreation(self):
        self.assertEqual(len(catalog.get_canteens()),3)
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute("INSERT INTO shops(canteen_id,name) VALUES (999,'invalid')")
        self.connection.rollback()
        self.connection.execute('DELETE FROM menu_options')
        self.connection.execute('DELETE FROM menu_items')
        self.connection.commit()
        self.assertEqual(catalog.get_menu_data('คณะครุศาสตร์','ร้านน้ำผลไม้')[1]['ร้านน้ำผลไม้'],{})
        self.assertEqual(self.connection.execute('SELECT count(*) FROM menu_items').fetchone()[0],0)


if __name__ == '__main__':
    unittest.main()
