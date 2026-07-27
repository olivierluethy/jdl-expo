"""
import_sql_dump_into_mysql.py — execute a large SQL dump against MySQL, statement by statement.

Description:
    Loads a generated dump into the database without needing the mysql client.
    The file is streamed one line at a time rather than read into memory, which
    matters because the dump it is aimed at is over forty megabytes. Comment
    lines and blank lines are skipped; every other line is appended to a buffer
    until a line ends with a semicolon, at which point the accumulated text is
    executed as one statement and the buffer is reset. The connection runs with
    autocommit enabled, so each statement is committed as it succeeds.

Requirements:
    - Python 3.x
    - Packages: mysql-connector-python
    - External services: a reachable MySQL server
    - Environment variables / credentials needed: none — the host, port, user,
      password and database name are hardcoded in this file, see SECURITY_NOTES.md

Inputs:
    database/dumps/tunevote_artists_and_videos_insert.sql

Outputs:
    No files. The effect is the rows written into the target database.

Usage:
    # from the repository root, with the virtual environment activated
    python database/parsers/import_sql_dump_into_mysql.py

Notes:
    Statement splitting is purely textual: a line is treated as the end of a
    statement whenever it ends in a semicolon, so a semicolon at the end of a
    line inside a quoted string would split it incorrectly. It is reliable for
    machine-generated dumps like the one it targets, not for arbitrary SQL.
    Because autocommit is on there is no surrounding transaction — an error
    halfway through leaves the already-executed statements applied, and the
    script will stop on the first failure. Importing the full dump takes a while.
"""

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
