# backend/db_config.py

import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        
        password="12345678",
        database="hello")
