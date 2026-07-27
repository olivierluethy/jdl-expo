import mysql.connector

# Verbindung zur MySQL-Datenbank (nicht phpMyAdmin!)
conn = mysql.connector.connect(
    # host="localhost",
    # host="72.167.49.141",
    host="127.0.0.1",
    port=3306,
    user="user",
    # password="__REDACTED__",
    password="__REDACTED__",
    # database="tunevote",
    database="easycontactforms",
)

cursor = conn.cursor()

# Alle Tabellen abrufen
cursor.execute("SHOW TABLES")
tables = [t[0] for t in cursor.fetchall()]

with open("database/dumps/tunevote_schema_structure.sql", "w", encoding="utf-8") as f:
    for table in tables:
        cursor.execute(f"SHOW CREATE TABLE `{table}`")
        create_stmt = cursor.fetchone()[1]
        f.write(f"-- Struktur für Tabelle `{table}`\n")
        f.write(create_stmt + ";\n\n")

cursor.close()
conn.close()