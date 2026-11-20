
import mysql.connector

def get_connection():

    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Tiger",
        database="student_placement",
        use_pure=True
    )

    return connection
