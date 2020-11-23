import sqlite3
import math

# Settings
connection = sqlite3.connect('persons.db')
cursor = connection.cursor()


def create_table():
    cursor.execute('CREATE TABLE IF NOT EXISTS persons(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, surname TXT, '
                   'h_11 REAL, h_12 REAL, h_21 REAL, h_22 REAL, h_31 REAL, h_32 REAL, h_41 REAL, h_42 REAL)')

    cursor.execute('CREATE TABLE IF NOT EXISTS users_Ratio(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id REAL, userRatioText TEXT, user_ratio REAL)')


def data_complete():
    connection.commit()
    cursor.close()
    connection.close()


def data_query(query = ""):
    create_table()
    result = cursor.execute(query)
    connection.commit()
    return result


def data_fetch(query = ""):
    create_table()
    cursor.execute(query)
    data = cursor.fetchall()

    return data

