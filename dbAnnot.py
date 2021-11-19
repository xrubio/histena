
#!/usr/bin/python3

import sqlite3 as sq 


def init():
    global conn
    conn = sq.connect("annot.db", check_same_thread=False)
    global db
    db = conn.cursor()


