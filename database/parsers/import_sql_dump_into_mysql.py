import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="user",
    password="userpass123!",
    database="tunevote",
    autocommit=True
)

cursor = conn.cursor()

with open("database/dumps/tunevote_artists_and_videos_insert.sql", "r", encoding="utf-8") as f:
    statement = ""
    for line in f:
        if line.startswith("--") or not line.strip():
            continue

        statement += line
        if line.rstrip().endswith(";"):
            cursor.execute(statement)
            statement = ""

cursor.close()
conn.close()
