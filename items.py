import db

def add_item(title, description, price, user_id):
    sql = """INSERT INTO items (title, description, price, user_id) VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, description, price, user_id])

def get_items():
    sql = "SELECT id, title FROM items ORDER BY id DESC"

    return db.query(sql)

def get_item(item_id):
    sql = """SELECT items.id,
                    items.title,
                    items.description,
                    items.price,
                    users.id user_id,
                    users.username
             FROM items, users
             WHERE items.user_id = users.id AND
                   items.id = ?"""
    return db.query(sql, [item_id])[0]

def update_item(item_id, title, description, price):
    sql = """UPDATE items SET title = ?,
                              description = ?,
                              price = ?
                          WHERE id = ?"""
    return db.execute(sql, [title, description, price, item_id])
