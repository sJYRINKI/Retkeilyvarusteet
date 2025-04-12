import db

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def add_pack(title, description, weight, price, user_id, classes):
    sql = """INSERT INTO packs (title, description, weight, price, user_id)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [title, description, weight, price, user_id])

    pack_id = db.last_insert_id()

    sql = "INSERT INTO pack_classes (pack_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [pack_id, title, value])

def add_comment(pack_id, user_id, comment):
    sql = """INSERT INTO comments (pack_id, user_id, comment)
             VALUES (?, ?, ?)"""
    db.execute(sql, [pack_id, user_id, comment])

def get_comments(pack_id):
    sql = """SELECT comments.id, comments.comment, users.id user_id, users.username
             FROM comments, users
             WHERE comments.pack_id = ? AND comments.user_id=users.id
             ORDER BY comments.id DESC"""
    return db.query(sql, [pack_id])

def check_comment(comment_id):
    sql = "SELECT id, pack_id, user_id FROM comments WHERE id = ?"
    result = db.query(sql, [comment_id])
    return result[0] if result else None

def remove_comment(comment_id):
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])

def get_images(pack_id):
    sql = "SELECT id FROM images WHERE pack_id = ?"
    return db.query(sql, [pack_id])

def add_image(pack_id, image):
    sql = "INSERT INTO images (pack_id, image) VALUES (?, ?)"
    db.execute(sql, [pack_id, image])

def get_image(image_id):
    sql = "SELECT image FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0][0] if result else None

def remove_image(pack_id, image_id):
    sql = "DELETE FROM images WHERE id = ? and pack_id = ?"
    db.execute(sql, [image_id, pack_id])

def get_classes(pack_id):
    sql = "SELECT title, value FROM pack_classes WHERE pack_id = ?"
    return db.query(sql, [pack_id])

def get_packs():
    sql = "SELECT id, title FROM packs ORDER BY id DESC"

    return db.query(sql)

def get_pack(pack_id):
    sql = """SELECT packs.id,
                    packs.title,
                    packs.description,
                    packs.weight,
                    packs.price,
                    users.id user_id,
                    users.username
             FROM packs, users
             WHERE packs.user_id = users.id AND
                   packs.id = ?"""
    result = db.query(sql, [pack_id])
    return result[0] if result else None

def update_pack(pack_id, title, description, weight, price, classes):
    sql = """UPDATE packs SET title = ?,
                              description = ?,
                              weight = ?,
                              price = ?
                          WHERE id = ?"""
    db.execute(sql, [title, description, weight, price, pack_id])

    sql = "DELETE FROM pack_classes WHERE pack_id = ?"
    db.execute(sql, [pack_id])

    sql = "INSERT INTO pack_classes (pack_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [pack_id, title, value])

def remove_pack(pack_id):
    sql = """DELETE FROM packs WHERE id = ?"""
    db.execute(sql, [pack_id])

def find_packs(query):
    sql = """SELECT id, title
             FROM packs
             WHERE title LIKE ? OR description LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])
