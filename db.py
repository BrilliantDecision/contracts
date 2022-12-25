import psycopg2
from psycopg2 import Error

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.create_connection()

    def __del__(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Соединение с PostgreSQL закрыто")

    def create_connection(self):
        try:
            # Подключение к существующей базе данных
            self.connection = psycopg2.connect(user="postgres",
                                          # пароль, который указали при установке PostgreSQL
                                          password="alexandr999",
                                          host="127.0.0.1",
                                          port="5432",
                                          database="postgres")

            # Курсор для выполнения операций с базой данных
            self.cursor = self.connection.cursor()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)

    def write_contracts(self, contracts):
        self.cursor.execute("""SELECT * FROM contracts""")
        records = self.cursor.fetch_all()
