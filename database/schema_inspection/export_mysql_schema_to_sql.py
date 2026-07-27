"""
export_mysql_schema_to_sql.py — dump the CREATE TABLE statements of a MySQL database to a .sql file.

Description:
    Connects directly to a MySQL server — not through phpMyAdmin — and captures
    the structure of the database without any of its data. It runs SHOW TABLES to
    enumerate the tables, then SHOW CREATE TABLE for each one, and writes every
    statement to a single SQL file with a comment header naming the table. The
    result is a schema-only snapshot that can be committed, diffed between
    environments, or replayed to recreate an empty copy of the database.

Requirements:
    - Python 3.x
    - Packages: mysql-connector-python
    - External services: a reachable MySQL server
    - Environment variables / credentials needed: none — the host, port, user,
      password and database name are hardcoded in this file, see SECURITY_NOTES.md

Inputs:
    The connection parameters at the top of this file. No arguments are parsed.

Outputs:
    database/dumps/tunevote_schema_structure.sql — overwritten on every run.

Usage:
    # from the repository root, with the virtual environment activated
    python database/schema_inspection/export_mysql_schema_to_sql.py

Notes:
    The connection block currently points at a local database and keeps the
    previous remote host, password and database name as commented-out lines just
    above the active ones; both sets of credentials are in plain text. They were
    deliberately left exactly as they are, because changing them would change
    which database the script talks to. The table name is interpolated straight
    into the SHOW CREATE TABLE query, which is safe here only because the names
    come from SHOW TABLES on the same server. The output file is overwritten
    without warning, so point it elsewhere before dumping a different database.
"""

import mysql.connector

# Connect to the MySQL server directly (not through phpMyAdmin)
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

# Retrieve the list of all tables
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