-- Run once on the existing canteen.db in DB Browser (Execute SQL).
-- Existing orders stay unassigned; no accounts are created by this script.
PRAGMA foreign_keys = ON;

SAVEPOINT add_users_migration;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL COLLATE NOCASE UNIQUE,
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('customer', 'shop')),
    shop_id INTEGER REFERENCES shops(shop_id),
    CHECK (
        (role = 'customer' AND shop_id IS NULL)
        OR (role = 'shop' AND shop_id IS NOT NULL)
    )
);

ALTER TABLE orders ADD COLUMN user_id INTEGER REFERENCES users(user_id);
ALTER TABLE orders ADD COLUMN shop_id INTEGER REFERENCES shops(shop_id);

CREATE INDEX orders_user_id_index ON orders(user_id);
CREATE INDEX orders_shop_id_index ON orders(shop_id);

RELEASE SAVEPOINT add_users_migration;

PRAGMA table_info(users);
PRAGMA table_info(orders);
