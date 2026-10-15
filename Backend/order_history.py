import sqlite3

from Backend import database, users


def read_orders():
    user = users.require_user('customer')
    connection = database.connect_database()
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute("""
            SELECT orders.*, COALESCE(SUM(unit_price * quantity), 0) AS total
            FROM orders LEFT JOIN order_items USING(order_id)
            WHERE orders.user_id = ?
            GROUP BY orders.order_id ORDER BY orders.order_id DESC
        """, (user["user_id"],))
        return [dict(row) for row in rows]
    finally:
        connection.close()


def read_details(order_id):
    user = users.require_user('customer')
    connection = database.connect_database()
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute('SELECT * FROM orders WHERE order_id = ? AND user_id = ?', (order_id, user['user_id'])).fetchone()
        if row is None:
            return None, []
        items = connection.execute(
            'SELECT * FROM order_items WHERE order_id = ? ORDER BY item_id', (order_id,),
        ).fetchall()
        return dict(row), [dict(item) for item in items]
    finally:
        connection.close()
