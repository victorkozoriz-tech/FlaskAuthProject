import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

username = "admin"
email = "admin@example.com"
password = generate_password_hash("admin123", method="pbkdf2:sha256")
role = "admin"
confirmed = True
avatar = "default.png"

cursor.execute("""
INSERT INTO user (username, email, password, role, confirmed, avatar)
VALUES (?, ?, ?, ?, ?, ?)
""", (username, email, password, role, confirmed, avatar))

conn.commit()
conn.close()

print("Admin user created successfully!")
