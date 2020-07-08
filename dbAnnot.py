
#!/usr/bin/python3

import sqlite3 as sq 


def init():
    global conn
    conn = sq.connect("annot.db")
    global db
    db = conn.cursor()


