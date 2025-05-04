import random
import sqlite3

db = sqlite3.connect("database.db")
cursor = db.cursor()

cursor.execute("DELETE FROM users")
cursor.execute("DELETE FROM packs")
cursor.execute("DELETE FROM pack_classes")
cursor.execute("DELETE FROM comments")

total_users = 10**4
total_packs = 10**5
total_comments = 10**6

for i in range(1, total_users + 1):
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                   (f"user{i}", f"hash{i}"))

for i in range(1, total_packs + 1):
    user_id = random.randint(1, total_users)
    cursor.execute("INSERT INTO packs (title, description, weight, price, user_id) VALUES (?, ?, ?, ?, ?)",
                   (f"Pack {i}", f"description {i}", 10, 10, user_id))

cursor.execute("SELECT id FROM packs")
pack_ids = [row[0] for row in cursor.fetchall()]

for i in range(1, total_comments + 1):
    user_id = random.randint(1, total_users)
    pack_id = random.choice(pack_ids)
    cursor.execute("INSERT INTO comments (pack_id, user_id, comment) VALUES (?, ?, ?)",
                   (pack_id, user_id, f"Comment {i}"))

db.commit()
db.close()
